import os
import random
import hashlib

from string import letters

from google.appengine.ext import db

import jinja2


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


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


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

# Add appropriate render functions


class Post(db.Model):
    user = db.ReferenceProperty(User, collection_name='posts')
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    creator_uid = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    user_liked = db.StringListProperty()

    @property
    def likes(self):
        likes = 0
        for uid in self.user_liked:
            likes += 1
        return likes

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
