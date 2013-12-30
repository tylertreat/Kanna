from google.appengine.ext import ndb

from flask import redirect
from flask import request

from kanna.api.blueprint import blueprint
from kanna.auth import get_session_user
from kanna.model import photo

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@blueprint.route("/v1/photos", methods=["POST"])
def upload():
    upload_file = request.files.get('file')
    image_data = upload_file.read()

    user = get_session_user()
    if not user:
        return '', 403

    if not image_data or not allowed_file(upload_file.filename):
        return '', 403

    uploaded = photo.upload(upload_file, image_data, user)

    return uploaded.json(size=250), 200


# TODO: this should require a DELETE request eventually w/o the /delete
@blueprint.route('/v1/photos/<photo_key>/delete')
def delete(photo_key):
    to_delete = ndb.Key(urlsafe=photo_key).get()
    if not to_delete:
        return '', 404

    user = get_session_user()
    if not user or to_delete.owner != user.key:
        return '', 403

    to_delete.key.delete()

    return redirect('/manage')


@blueprint.route('/v1/photos/<photo_key>', methods=['POST'])
def update(photo_key):
    to_update = ndb.Key(urlsafe=photo_key).get()
    if not to_update:
        return '', 404

    user = get_session_user()
    if not user or to_update.owner != user.key:
        return '', 403

    to_update.name = request.form['name']
    to_update.description = request.form['description']
    to_update.location = request.form['location']
    to_update.put()

    return redirect('/manage')

