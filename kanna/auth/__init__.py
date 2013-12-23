from google.appengine.api import users

from kanna.model.user import User


def get_session_user():
    """Retrieve the current session user. If a user entity does not exist for
    the account (i.e. first time logging in), create one. Returns None if a
    user is not currently logged in.

    Returns:
        the current session user.
    """

    gae_user = users.get_current_user()
    if not gae_user:
        # User is not logged in
        return None

    # TODO: handle TransactionFailedErrors
    user = User.get_by_id(gae_user.user_id())
    if not user:
        user = User(id=gae_user.user_id(), email=gae_user.email())
        user.put()

    return user

