from flask import Blueprint
from flask import flash
from flask import g
import os
import json
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.exceptions import abort

from .auth import login_required
from . import site
from . import message
from ..models import User, Message, db
from ..forms import NameForm


@message.route("/message/")
def index():
    """Show all the msg for a business user."""
    user_id = session.get("user_id")
    messages = Message.query.filter_by(user_id = user_id).all()

    return render_template("blog/index.html", messages=messages)

# delete all messages with user_id and secret key of the site
@message.route("/message/delete/<user_id>/<key>")
def delete(user_id, key):
    """deelte all the postsof a user id."""
    # user_id = session.get("user_id")
    if key == os.environ['JWT_SECRET_KEY']:
        # messages = Message.query.filter_by(user_id = user_id).all()
        messages = Message.__table__.delete().where(Message.user_id == user_id)
        db.session.execute(messages)
        db.session.commit()
    return index()

@message.route('/message/save/<user_id>/<key>')
def save(user_id, key):
    if key == os.environ['JWT_SECRET_KEY']:
        messages = json.dumps(Message.query.filter_by(user_id = user_id).all(), default = myconverter)
        # write into a file
        for folder in ['dumps', 'dumps/' + user_id]:
            if not os.path.exists(folder):
                os.makedirs(folder)

        f = open("dumps/" + user_id + "/messages.txt", "w+")
        f.write(messages)
        f.close()
    return index()


# date time serializer for json.dumps
def myconverter(o):
    if not isinstance(o, str):
        return o.__str__()

# def get_post(id, check_author=True):
#     """Get a post and its author by id.

#     Checks that the id exists and optionally that the current user is
#     the author.

#     :param id: id of post to get
#     :param check_author: require the current user to be the author
#     :return: the post with author information
#     :raise 404: if a post with the given id doesn't exist
#     :raise 403: if the current user isn't the author
#     """
#     post = (
    
#         .execute(
#             "SELECT p.id, title, body, created, author_id, username"
#             " FROM post p JOIN user u ON p.author_id = u.id"
#             " WHERE p.id = ?",
#             (id,),
#         )
#         .fetchone()
#     )

#     if post is None:
#         abort(404, f"Post id {id} doesn't exist.")

#     if check_author and post["author_id"] != g.user["id"]:
#         abort(403)

#     return post


# @message.route("/create", methods=("GET", "POST"))
# @login_required
# def create():
#     """Create a new post for the current user."""
#     if request.method == "POST":
#         title = request.form["title"]
#         body = request.form["body"]
#         error = None

#         if not title:
#             error = "Title is required."

#         if error is not None:
#             flash(error)
#         else:

#             db.execute(
#                 "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
#                 (title, body, g.user["id"]),
#             )
#             db.commit()
#             return redirect(url_for("blog.index"))

#     return render_template("blog/create.html")


# @message.route("/<int:id>/update", methods=("GET", "POST"))
# @login_required
# def update(id):
#     """Update a post if the current user is the author."""
#     post = get_post(id)

#     if request.method == "POST":
#         title = request.form["title"]
#         body = request.form["body"]
#         error = None

#         if not title:
#             error = "Title is required."

#         if error is not None:
#             flash(error)
#         else:
#             db.execute(
#                 "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
#             )
#             db.commit()
#             return redirect(url_for("blog.index"))

#     return render_template("blog/update.html", post=post)


# @message.route("/<int:id>/delete", methods=("POST",))
# @login_required
# def delete(id):
#     """Delete a post.

#     Ensures that the post exists and that the logged in user is the
#     author of the post.
#     """
#     get_post(id)

#     db.execute("DELETE FROM post WHERE id = ?", (id,))
#     db.commit()
#     return redirect(url_for("blog.index"))
