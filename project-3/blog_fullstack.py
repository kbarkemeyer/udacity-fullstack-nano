import os
import re
import random
import hashlib
import hmac

from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

secret = 'deissu'


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())


def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

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


# user stuff

def make_salt(length=5):
    return ''.join(random.choice(letters) for x in xrange(length))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)


def users_key(group='default'):
    return db.Key.from_path('users', group)


class User(db.Model):
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent=users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent=users_key(),
                    name=name,
                    pw_hash=pw_hash,
                    email=email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u

# blog stuff
# Add appropriate render functions


class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    creator_uid = db.StringProperty(required=True)
    creator_name = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    likes = db.IntegerProperty()
    user_liked = db.StringListProperty()

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p=self)

    def render_own_post(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("own_post.html", p=self)

    def render_liked_post(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("liked_post.html", p=self)

    def render_user_post(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("user_post.html", p=self)


# Add Comment model, comments are reference properties which refer
# to respective posts, thus establishing a many to one relationship.


class Comment(db.Model):
    post = db.ReferenceProperty(Post, collection_name='comments')
    comment_text = db.TextProperty()
    comment_author = db.TextProperty()
    comment_uid = db.StringProperty(required=True)

    def render_comment_text(self):
        self.comment_text.replace('\n', '<br>')


class BlogFront(BlogHandler):
    def get(self):
        posts = Post.all().order('-created')
        if not self.user:
            self.render('front.html', posts=posts, uid=None)
        else:
            uid = self.read_secure_cookie('user_id')
            self.render('front.html', posts=posts, uid=uid)


class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)

        if not post:
            self.error(404)
            return

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
            self.redirect('/blog')

        uid = self.read_secure_cookie('user_id')
        current_user = User.by_id(int(uid))
        name = current_user.name
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(subject=subject, content=content, creator_uid=uid,
                     creator_name=name, likes=0)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content,
                        error=error)


# Add edit post handler


class EditPost(NewPost):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)
        uid = self.read_secure_cookie('user_id')

        if not post:
            self.error(404)
            return

        if post.creator_uid == uid:
            subject = post.subject
            content = post.content

            self.render("editpost.html", subject=subject, content=content,
                        post=post)

        else:
            message = "You can only edit your own post!"
            self.render("editpost.html", subject=subject, content=content,
                        error=message)

    def post(self, post_id):
        if not self.user:
            self.redirect('/blog')

        key = db.Key.from_path('Post', int(post_id))
        p = db.get(key)
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p.subject = subject
            p.content = content
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))

        else:
            error = "subject and content, please!"
            self.render("editpost.html", subject=subject, content=content,
                        error=error)

# Add delete post handler


class DeletePost(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)
        uid = self.read_secure_cookie('user_id')

        if not post:
            self.error(404)
            return

        if uid == post.creator_uid:
            message = "Are you sure you want to delete this post?"
            self.render("deletepost.html", post=post, uid=uid, message=message)

        else:
            message = "You are not authorized to delete this post!"
            self.render("permalink.html", post=post, uid=uid, error=message)

    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)
        post_comments = post.comments.get()
        if post_comments:
            post_comments.delete()
        post.delete()
        self.redirect('/blog')


# Add like post handler


class LikePost(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)
        uid = self.read_secure_cookie('user_id')

        if not post:
            self.error(404)
            return

        if uid == post.creator_uid:
            message = "You cannot like or unlike your own post!"
            self.render("permalink.html", post=post, uid=uid, error=message)

        else:
            message = "Please click on the buttons to like or dislike post!"
            self.render("permalink.html", post=post, uid=uid, error=message)

    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)
        uid = self.read_secure_cookie('user_id')

        if not post:
            self.error(404)
            return

        post.likes += 1
        post.user_liked.append(uid)
        post.put()

    def delete(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)
        uid = self.read_secure_cookie('user_id')

        if not post:
            self.error(404)
            return

        post.likes -= 1
        post.user_liked.remove(uid)
        post.put()


# Add comment handler


class PostComment(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("postcomment.html", post=post)

    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)
        uid = self.read_secure_cookie('user_id')
        current_user = User.by_id(int(uid))

        if not self.user:
            self.redirect('/blog')

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
    def get(self, c_id):
        c_key = db.Key.from_path('Comment', int(c_id))
        c = db.get(c_key)
        post_id = Comment.post.get_value_for_datastore(c).id()
        p_key = db.Key.from_path('Post', int(post_id))
        post = db.get(p_key)
        uid = self.read_secure_cookie('user_id')

        if not c:
            self.error(404)
            return
        if c.comment_uid == uid:
            c_text = c.comment_text
            self.render("postcomment.html", comment=c_text, post=post)
        else:
            message = "You can only edit your own comment!"
            self.render("permalink.html", uid=uid, post=post,
                        error=message)

    def post(self, c_id):
        if not self.user:
            self.redirect('/blog')

        c_key = db.Key.from_path('Comment', int(c_id))
        c = db.get(c_key)
        comment = self.request.get('comment')
        post_id = Comment.post.get_value_for_datastore(c).id()

        if comment:
            c.comment_text = comment
            c.put()
            self.redirect('/blog/%s' % str(post_id))
        else:
            message = "Content, please!"
            self.render("postcomment.html", comment=comment, error=message)


# Add delete comment handler


class DeleteComment(BlogHandler):
    def get(self, c_id):
        c_key = db.Key.from_path('Comment', int(c_id))
        c = db.get(c_key)
        post_id = Comment.post.get_value_for_datastore(c).id()
        p_key = db.Key.from_path('Post', int(post_id))
        post = db.get(p_key)
        uid = self.read_secure_cookie('user_id')

        if not c:
            self.error(404)
            return
        if c.comment_uid == uid:
            c.delete()
            self.redirect('/blog/%s' % str(post_id))
        else:
            message = "You can only delete your own comment!"
            self.render("permalink.html", uid=uid, post=post, error=message)


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
