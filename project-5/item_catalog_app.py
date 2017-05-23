from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash
from flask import session as login_session

from functools import wraps

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

from item_catalog_db import Base, Bookbin, Book, Reader

import random
import string
import json
import pycurl
import urllib
import StringIO

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('amazon_client_id_secret.json', 'r').read())['a']['client_id']

# Connect to Database and create database session
engine = create_engine('sqlite:///bookrecommendations.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Decorator function checking if user is logged in
def login_required(f):
    """ Decorator function checking if user is logged in """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'readername' not in login_session:
            return redirect(url_for('showLogin'))
        return f(*args, **kwargs)
    return decorated_function


# Create anti_forgery state token
@app.route('/login')
def showLogin():
    """ Return Login page with state parameter """

    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('bookappLogin.html', state=state)


# Implement login with amazon
@app.route('/amazonconnect', methods=['GET', 'POST'])
def amazonConnect():
    """ Verify Amazon access token, exchange it for user profile.
        Redirect logged user to Bookbin main page """

    # Validate token
    if request.args.get('state') != login_session['state']:
        flash('Login failed! Please try again!')
        return redirect(url_for('showBookbins'))

    access_token = request.args.get('access_token')

    b = StringIO.StringIO()
    # verify that the access token belongs to us
    c = pycurl.Curl()
    c.setopt(pycurl.URL,
             "https://api.amazon.com/auth/o2/tokeninfo?access_token=" +
             urllib.quote_plus(access_token))
    c.setopt(pycurl.SSL_VERIFYPEER, 1)
    c.setopt(pycurl.WRITEFUNCTION, b.write)

    c.perform()
    d = json.loads(b.getvalue())

    if d['aud'] != CLIENT_ID:
        # the access token does not belong to us
        raise BaseException("Invalid Token")

    # exchange the access token for user profile
    b = StringIO.StringIO()

    c = pycurl.Curl()
    c.setopt(pycurl.URL, "https://api.amazon.com/user/profile")
    c.setopt(pycurl.HTTPHEADER, ["Authorization: bearer " + access_token])
    c.setopt(pycurl.SSL_VERIFYPEER, 1)
    c.setopt(pycurl.WRITEFUNCTION, b.write)

    c.perform()
    d = json.loads(b.getvalue())

    login_session['readername'] = d['name']
    login_session['email'] = d['email']
    # In case different providers are added later
    login_session['provider'] = 'amazon'

    reader_id = getReaderID(login_session['email'])
    if not reader_id:
        reader_id = createReader(login_session)
    login_session['reader_id'] = reader_id

    flash("Welcome! You are logged in as %s" % login_session['readername'])

    return redirect(url_for('showBookbins'))


@app.route('/amazondisconnect')
def amazonDisconnect():
    """ Log out user, remove from login_session and redirect to
        public bookbin page """

    if 'readername' in login_session:
        del login_session['readername']
        del login_session['email']
        del login_session['reader_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showBookbins'))
    else:
        flash("You were not logged in.")
        return redirect(url_for('showBookbins'))


# JSON APIs to view Bookbin information
@app.route('/bookbin/JSON')
def showBookbinsJSON():
    """ Return bookbins as JSON object """

    bookbins = session.query(Bookbin).order_by(asc(Bookbin.name))
    return jsonify(bookbins=[b.serialize for b in bookbins])


@app.route('/bookbin/<int:bookbin_id>/books/JSON')
def showBooksJSON(bookbin_id):
    """ Return books of respective bookbin as JSON object """

    books = session.query(Book).filter_by(bookbin_id=bookbin_id).order_by(
        asc(Book.title)).all()
    return jsonify(books=[b.serialize for b in books])


@app.route('/')
@app.route('/bookbin/')
def showBookbins():
    """ Return all bookbins """

    bookbins = session.query(Bookbin).order_by(asc(Bookbin.name))
    if 'readername' not in login_session:
        return render_template('publicbookbins.html', bookbins=bookbins)
    else:
        return render_template('bookbins.html', bookbins=bookbins)


@app.route('/bookbin/new/', methods=['GET', 'POST'])
@login_required
def newBookbin():
    """ Add new bookbin to database"""

    if request.method == 'POST':
        newBookbin = Bookbin(name=request.form['name'],
                             reader_id=login_session['reader_id'])
        if not newBookbin.name:
            flash("Bookbin name is required!")
            return render_template('newBookbin.html')
        session.add(newBookbin)
        flash('New Bookbin %s Successfully Created' % newBookbin.name)
        session.commit()
        return redirect(url_for('showBookbins'))
    else:
        return render_template('newBookbin.html')


# Edit a bookbin
@app.route('/bookbin/<int:bookbin_id>/edit/', methods=['GET', 'POST'])
@login_required
def editBookbin(bookbin_id):
    """ Edit current bookbin"""
    try:
        bookbin = session.query(Bookbin).filter_by(id=bookbin_id).one()

        if login_session['reader_id'] != bookbin.reader_id:
            flash('You are not authorized to edit this item!')
            return redirect(url_for('showBookbins'))

        editedBookbin = session.query(Bookbin).filter_by(id=bookbin_id).one()
        if request.method == 'POST':
            if request.form['name']:
                editedBookbin.name = request.form['name']
                flash('Bookbin Successfully Edited %s' % editedBookbin.name)
                return redirect(url_for('showBookbins'))
        else:
            return render_template('editBookbin.html', bookbin=editedBookbin)
    except:
        return redirect(url_for('showBookbins'))


# Delete a bookbin
@app.route('/bookbin/<int:bookbin_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteBookbin(bookbin_id):
    """ Delete current bookbin """
    try:
        bookbin = session.query(Bookbin).filter_by(id=bookbin_id).one()

        if login_session['reader_id'] != bookbin.reader_id:
            flash('You are not authorized to edit this item!')
            return redirect(url_for('showBookbins'))

        bookbinToDelete = session.query(Bookbin).filter_by(id=bookbin_id).one()

        if request.method == 'POST':
            session.delete(bookbinToDelete)
            flash('%s Successfully Deleted' % bookbinToDelete.name)
            session.commit()
            return redirect(url_for('showBookbins'))
        else:
            return render_template('deleteBookbin.html',
                                   bookbin=bookbinToDelete)
    except:
        return redirect(url_for('showBookbins'))


# Show a bookbin's books
@app.route('/bookbin/<int:bookbin_id>/')
@app.route('/bookbin/<int:bookbin_id>/books/')
def showBooks(bookbin_id):
    """ Return all books in respective bookbin"""
    try:
        bookbin = session.query(Bookbin).filter_by(id=bookbin_id).one()

        creator = getReaderInfo(bookbin.reader_id)
        books = session.query(Book).filter_by(bookbin_id=bookbin_id).order_by(
            asc(Book.title)).all()
        if 'readername' not in login_session or creator.id != login_session[
                'reader_id']:
            return render_template('publicBooks.html', books=books,
                                   bookbin=bookbin, creator=creator.name)
        else:
            return render_template('books.html', books=books, bookbin=bookbin,
                                   creator=creator.name)
    except:
        return redirect(url_for('showBookbins'))


# Create a new book
@app.route('/bookbin/<int:bookbin_id>/books/new/', methods=['GET', 'POST'])
@login_required
def newBook(bookbin_id):
    """ Add new book to respective bookbin """
    try:
        bookbin = session.query(Bookbin).filter_by(id=bookbin_id).one()

        if login_session['reader_id'] != bookbin.reader_id:
            flash('You are not authorized to edit this item!')
            return redirect(url_for('showBookbins'))

        if request.method == 'POST':
            newBook = Book(title=request.form['title'],
                           author=request.form['author'],
                           pub_year=request.form['pub_year'],
                           description=request.form['description'],
                           genre=request.form['genre'],
                           bookbin_id=bookbin_id,
                           reader_id=login_session['reader_id'])
            if not newBook.title:
                flash('A book title is required!')
                return render_template('newBook.html', bookbin_id=bookbin_id)
            session.add(newBook)
            session.commit()
            flash('New Book %s Successfully Created' % (newBook.title))
            return redirect(url_for('showBooks', bookbin_id=bookbin_id))
        else:
            return render_template('newBook.html', bookbin_id=bookbin_id)

    except:
        return redirect(url_for('showBookbins'))


# Edit a book
@app.route('/bookbin/<int:bookbin_id>/books/<int:book_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editBook(bookbin_id, book_id):
    """ Edit respective book """
    try:
        bookbin = session.query(Bookbin).filter_by(id=bookbin_id).one()

        if login_session['reader_id'] != bookbin.reader_id:
            flash('You are not authorized to edit this item!')
            return redirect(url_for('showBookbins'))

        editedBook = session.query(Book).filter_by(id=book_id).one()

        if not editedBook:
            return redirect(url_for('showBookbins'))

        creator = getReaderInfo(bookbin.reader_id)

        if request.method == 'POST':
            if request.form['title']:
                editedBook.title = request.form['title']
            if request.form['author']:
                editedBook.author = request.form['author']
            if request.form['description']:
                editedBook.description = request.form['description']
            if request.form['genre']:
                editedBook.genre = request.form['genre']
            if request.form['pub_year']:
                editedBook.pub_year = request.form['pub_year']
            session.add(editedBook)
            session.commit()
            flash('Book Successfully Edited')
            return redirect(url_for('showBooks', bookbin_id=bookbin_id,
                            creator=creator.name))
        else:
            return render_template('editBook.html', bookbin=bookbin,
                                   book=editedBook)

    except:
        return redirect(url_for('showBookbins'))



# Delete a book
@app.route('/bookbin/<int:bookbin_id>/books/<int:book_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteBook(bookbin_id, book_id):
    """ Delete respective book """
    try:
        bookbin = session.query(Bookbin).filter_by(id=bookbin_id).one()

        if login_session['reader_id'] != bookbin.reader.id:
            flash('You are not authorized to edit this item!')
            return redirect(url_for('showBookbins'))

        creator = getReaderInfo(bookbin.reader_id)

        bookToDelete = session.query(Book).filter_by(id=book_id).one()

        if request.method == 'POST':
            session.delete(bookToDelete)
            session.commit()
            flash('Book Successfully Deleted')
            return redirect(url_for('showBooks', bookbin_id=bookbin_id,
                            creator=creator.name))
        else:
            return render_template('deleteBook.html', bookbin_id=bookbin_id,
                                   book=bookToDelete)

    except:
        return redirect(url_for('showBookbins'))




# Reader stuff

def getReaderID(email):
    """ Return reader_id wif reader logged in current session """

    try:
        reader = session.query(Reader).filter_by(email=email).one()
        return reader.id
    except:
        return None


def getReaderInfo(reader_id):
    """ Return reader object """

    reader = session.query(Reader).filter_by(id=reader_id).one()
    return reader


def createReader(login_session):
    """ Create new reader """

    newReader = Reader(name=login_session['readername'],
                       email=login_session['email'])
    session.add(newReader)
    session.commit()
    reader = session.query(Reader).filter_by(
        email=login_session['email']).one()
    return reader.id


if __name__ == '__main__':
    app.secret_key = 'deissu'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
