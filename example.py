from flask import Flask, redirect, url_for, session, request, jsonify, render_template
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'

oauth = OAuth(app)

infusionsoft = oauth.remote_app(
    'infusionsoft',
    consumer_key='',        # client_id
    consumer_secret='',     # client_secret
    base_url='https://api.infusionsoft.com/crm/rest/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://api.infusionsoft.com/token',
    authorize_url='https://signin.infusionsoft.com/app/oauth/authorize'
)

@app.route('/')
def index():
    isAuthenticated = 'infusionsoft_token' in session

    return render_template('index.html', isAuthenticated=isAuthenticated)

@app.route('/contacts', methods=['POST'])
def add_contact():
    headers = {'Content-Type': 'application/json'}
    contact = infusionsoft.post('contacts', data={
        'given_name':       request.form.get('given_name'),
        'family_name':      request.form.get('family_name'),
        'email_addresses':  [{'field': 'EMAIL1', 'email': request.form.get('email')}],
        'opt_in_reason':    'Testing Contact Add via Rest'
    }, headers=headers, format='json')
    return jsonify(contact.data)

@app.route('/login')
def login():
    return infusionsoft.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('infusionsoft_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = infusionsoft.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )
    session['infusionsoft_token'] = (resp['access_token'], '')
    me = infusionsoft.get('contacts')
    return jsonify(me.data)


@infusionsoft.tokengetter
def get_infusionsoft_oauth_token():
    return session.get('infusionsoft_token')


if __name__ == '__main__':
    app.run()