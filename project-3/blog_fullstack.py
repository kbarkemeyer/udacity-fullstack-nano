import os
import re
import hmac

from functools import wraps

from models import User
from models import Post
from models import Comment

from google.appengine.ext import db

import webapp2
import jinja2


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

secret = 'deissu'


# secure val functions

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())


def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


# decorator helper functions

def post_exists(function):
    @wraps(function)
    def check_post(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)
        status = 200
        if post:
            return function(self, post, status)
        else:
            status = 404
            return function(self, post, status)
    return check_post


def user_owns_post(function):
    @wraps(function)
    def user_post(self, post, status):
        uid = self.read_secure_cookie('user_id')
        if status == 200:
            creator_uid = post.creator_uid
            if post.creator_uid == uid:
                return function(self, post, uid, creator_uid, status)
        else:
            status = 404
            return function(self, post, uid, status)
    return user_post


def comment_exists(function):
    @wraps(function)
    def comment(self, c_id):
        c_key = db.Key.from_path('Comment', int(c_id))
        c = db.get(c_key)
        if c:
            post_id = Comment.post.get_value_for_datastore(c).id()
            p_key = db.Key.from_path('Post', int(post_id))
            post = db.get(p_key)
            status = 200
            return function(self, status, c, post_id, post)
        else:
            status = 404
            return function(self, status)
    return comment


def user_owns_comment(function):
    @wraps(function)
    def user_comment(self, status, c=None, post_id=None, post=None):
        if status == 404:
            return function(self, status)
        else:
            uid = self.read_secure_cookie('user_id')
            if c.comment_uid == uid:
                c_text = c.comment_text
                return function(self, status, c, post, post_id, uid, c_text)
            else:
                return function(self, status, c, post, post_id, uid)
    return user_comment


# Main Blog handler


class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


# Other Blog handlers


class BlogFront(BlogHandler):
    def get(self):
        posts = Post.all().order('-created')
        if not self.user:
            self.render('front.html', posts=posts, uid=None)
        else:
            uid = self.read_secure_cookie('user_id')
            self.render('front.html', posts=posts, uid=uid)


class PostPage(BlogHandler):
    @post_exists
    def get(self, post, status):
        if status == 404:
            return self.redirect('/blog')
        else:
            if not self.user:
                self.render("permalink.html", post=post, uid=None)
            else:
                uid = self.read_secure_cookie('user_id')
                self.render("permalink.html", post=post, uid=uid)


class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/login')

        else:
            uid = self.read_secure_cookie('user_id')
            subject = self.request.get('subject')
            content = self.request.get('content')

            if subject and content:
                p = Post(user=self.user, subject=subject, content=content,
                         creator_uid=uid, likes=0)
                p.put()
                self.redirect('/blog/%s' % str(p.key().id()))
            else:
                error = "subject and content, please!"
                self.render("newpost.html", subject=subject, content=content,
                            error=error)


# Add edit post handler


class EditPost(NewPost):
    @post_exists
    @user_owns_post
    def get(self, post, uid, status, creator_uid=None):
        if status == 404:
            return self.redirect("/blog")

        if not self.user:
            return self.redirect("/login")

        else:
            if not post.creator_uid:
                message = "You can only edit your own post!"
                self.render("permalink.html", post=post, uid=uid,
                            error=message)

            else:
                subject = post.subject
                content = post.content
                self.render("editpost.html", subject=subject, content=content,
                            post=post)

    @post_exists
    def post(self, post, status):
        if status == 404:
            return self.redirect("/blog")

        if not self.user:
            self.redirect('/login')

        else:
            subject = self.request.get('subject')
            content = self.request.get('content')

            if subject and content:
                post.subject = subject
                post.content = content
                post.put()
                self.redirect('/blog/%s' % str(post.key().id()))

            else:
                error = "subject and content, please!"
                self.render("editpost.html", subject=subject, content=content,
                            error=error)

# Add delete post handler


class DeletePost(BlogHandler):
    @post_exists
    @user_owns_post
    def get(self, post, uid, status, creator_uid=None):
        if status == 404:
            return self.redirect("/blog")

        if not self.user:
            return self.redirect("/login")

        else:
            if not creator_uid:
                message = "You are not authorized to delete this post!"
                self.render("permalink.html", post=post, uid=uid,
                            error=message)

            else:
                message = "Are you sure you want to delete this post?"
                self.render("deletepost.html", post=post, uid=uid,
                            message=message)

    @post_exists
    def post(self, post, status):
        if status == 404:
            return self.redirect("/blog")

        if not self.user:
            return self.redirect("/login")

        else:
            post_comments = post.comments.get()
            if post_comments:
                post_comments.delete()
            post.delete()
            self.redirect('/blog')


# Add like post handler


class LikePost(BlogHandler):
    @post_exists
    def get(self, post, status):
        uid = self.read_secure_cookie('user_id')

        if status == 404:
            return self.redirect("/blog")

        if not self.user:
            return self.redirect("/login")

        if uid == post.creator_uid:
            message = "You cannot like or unlike your own post!"
            self.render("permalink.html", post=post, uid=uid, error=message)

        else:
            message = "Please click on the buttons to like or dislike post!"
            self.render("permalink.html", post=post, uid=uid, error=message)

    @post_exists
    def post(self, post, status):
        uid = self.read_secure_cookie('user_id')

        if status == 404:
            return self.redirect("/blog")

        if not self.user:
            return self.redirect("/login")

        else:
            post.user_liked.append(uid)
            post.put()

    @post_exists
    def delete(self, post, status):
        uid = self.read_secure_cookie('user_id')

        if status == 404:
            return self.redirect("/blog")

        if not self.user:
            return self.redirect("/login")

        else:
            post.user_liked.remove(uid)
            post.put()


# Add comment handler


class PostComment(BlogHandler):
    @post_exists
    def get(self, post, status):
        if status == 404:
            return self.redirect("/blog")

        if not self.user:
            return self.redirect("/login")

        else:
            self.render("postcomment.html", post=post)

    @post_exists
    def post(self, post, status):
        uid = self.read_secure_cookie('user_id')
        current_user = User.by_id(int(uid))

        if status == 404:
            return self.redirect("/blog")

        if not self.user:
            return self.redirect("/login")

        else:
            comment = self.request.get('comment')

            if comment:
                c = Comment(post=post, comment_text=comment,
                            comment_author=current_user.name, comment_uid=uid)
                c.put()
                self.redirect('/blog')
            else:
                self.redirect('/blog')


# Add edit comment handler


class EditComment(BlogHandler):
    @comment_exists
    @user_owns_comment
    def get(self, status, c=None, post=None, post_id=None, uid=None,
            c_text=None):
        if not self.user:
            self.redirect('/login')

        if status == 404:
            self.redirect('/blog')

        else:
            if not c_text:
                message = "You can only edit your own comment!"
                self.render("permalink.html", uid=uid, post=post,
                            comment=c_text, error=message)

            else:
                self.render("postcomment.html", uid=uid, comment=c_text,
                            post=post)

    @comment_exists
    @user_owns_comment
    def post(self, status, c=None, post=None, post_id=None, uid=None,
             c_text=None):
        if not self.user:
            self.redirect('/login')

        if status == 404:
            self.redirect('/blog')

        else:
            if not c_text:
                message = "You can only edit your own comment!"
                self.render("permalink.html", uid=uid, post=post,
                            error=message)

            else:
                comment = self.request.get('comment')
                if comment:
                    c.comment_text = comment
                    c.put()
                    self.redirect('/blog/%s' % str(post_id))
                else:
                    message = "Content, please!"
                    self.render("postcomment.html", error=message)


# Add delete comment handler


class DeleteComment(BlogHandler):
    @comment_exists
    @user_owns_comment
    def get(self, status, c=None, post=None, post_id=None, uid=None,
            c_text=None):
        if not self.user:
            self.redirect('/login')

        if status == 404:
            self.redirect('/blog')

        else:
            if not c_text:
                message = "You can only delete your own comment!"
                self.render("permalink.html", uid=uid, post=post,
                            error=message)

            else:
                c.delete()
                self.redirect('/blog/%s' % str(post_id))


# user signup


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")


def valid_username(username):
    return username and USER_RE.match(username)


PASS_RE = re.compile(r"^.{3,20}$")


def valid_password(password):
    return password and PASS_RE.match(password)


EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


def valid_email(email):
    return not email or EMAIL_RE.match(email)


class Signup(BlogHandler):
    def get(self):
        self.render("sign_up.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username=self.username, email=self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('sign_up.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError


class Register(Signup):
    def done(self):
        # make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('sign_up.html', error_username=msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/blog')


# Login/Logout


class Login(BlogHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/blog')
        else:
            msg = 'Invalid login'
            self.render('login.html', error=msg)


class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/signup')


app = webapp2.WSGIApplication([
                             ('/blog', BlogFront),
                             ('/blog/([0-9]+)', PostPage),
                             ('/blog/newpost', NewPost),
                             ('/blog/edit/([0-9]+)', EditPost),
                             ('/blog/delete/([0-9]+)', DeletePost),
                             ('/blog/comment/([0-9]+)', PostComment),
                             ('/blog/comment/edit/([0-9]+)', EditComment),
                             ('/blog/comment/delete/([0-9]+)', DeleteComment),
                             ('/blog/like/([0-9]+)', LikePost),
                             ('/signup', Register),
                             ('/login', Login),
                             ('/logout', Logout),
                              ],
                              debug=True)
