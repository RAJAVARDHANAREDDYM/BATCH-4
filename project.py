#!/usr/bin/env python3
from flask import Flask, url_for, render_template
from flask import request, redirect, jsonify, flash
from flask import session as login_session
import random
import string
import requests
import os
import re


from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from database_setup import User, Base

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Auto.QuestionPaper.Generator"

engine = create_engine(
    'sqlite:///questionpaper.db',
    connect_args={
        'check_same_thread': False},
    echo=True)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


@app.route('/')
def main():
	return render_template('main.html')


@app.route('/showi')
def show():
	return ("<h1> Loged in Successfully </h1>")


def createUser(login_session, role):
	name = login_session['username']
	email = login_session['email']
	user_pic = login_session['picture']
	data = User(name=name, email=email, user_pic=user_pic, role=role)
	session.add(data)
	session.commit()
	data = session.query(User).filter_by(email=email).one()
	flash("New User " + name + " created")
	return data.id


def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(
            string.ascii_uppercase +
            string.digits +
            string.ascii_lowercase) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        print("result['user_id'] is:", result['user_id'])
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        print(result['issued_to'])
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserId(login_session['email'])
    if not user_id:
        count = 0
        if re.match("[0-9a-zA-Z.]*@gmail.com", data['email']):
            role = "Faculty"
            count = 1
            print(role)
        if re.match("1[^a-zA-Z]4g[1,5]a0[1-5]\w\d@srit.ac.in",data['email']):
            role="student";
            count=1
            print(role)
        if count == 0:
            return("<h1> Login with srit.ac.in domain </h1>")
        user_id = createUser(login_session,role)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print ('In gdisconnect access token is %s', access_token)
    # print 'User name is: '
    # print login_session['username']
    b = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % b
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print (result)
    print (login_session)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
