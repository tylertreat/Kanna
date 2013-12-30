from flask import redirect
from flask import request

from kanna.api.blueprint import blueprint
from kanna.auth import get_session_user
from kanna.model.photo import Album


@blueprint.route("/v1/albums", methods=["POST"])
def new_album():
    name = request.form['name']
    description = request.form.get('description')

    user = get_session_user()
    if not user:
        return '', 403

    existing = Album.get_by_id('%s_%s' % (user.key.id(), name.lower()))
    if existing:
        return '', 409

    album = Album(name=name, description=description, owner=user.key)
    album.put()

    return redirect('/manage')

