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

    photo.upload(upload_file, image_data, user)

    return redirect('/')

