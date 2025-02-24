# Google OAuth Implementation

from flask import redirect, url_for
from authlib.integrations.flask_client import OAuth
from config.config import Config

oauth = OAuth()

def init_oauth(app):
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=Config.GOOGLE_CLIENT_ID,
        client_secret=Config.GOOGLE_CLIENT_SECRET,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_params=None,
        refresh_token_url=None,
        redirect_uri=url_for('google_auth_callback', _external=True),
        client_kwargs={'scope': 'email profile'}
    )

def google_login():
    return oauth.google.authorize_redirect()

def google_auth_callback():
    token = oauth.google.authorize_access_token()
    # TODO: Process user information from token
    return redirect(url_for('index'))
