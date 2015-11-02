from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, SupplyItem


# IMPORTS FOR LOGIN
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Cat Supplies Catalog App"

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
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

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response



engine = create_engine('sqlite:///catsupplies.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catsupplies/')
def listCategories():
	categories = session.query(Category).all()

	return render_template('categories.html', categories = categories)


@app.route('/catsupplies/new/', methods = ['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
	if request.method == 'POST':
		if request.form['name']:
			newCategory = Category(name = request.form['name'])
			session.add(newCategory)
			session.commit()
			flash("New category created!")
			return redirect(url_for('listCategories'))
	else:	
		return render_template('newCategory.html')


@app.route('/catsupplies/<int:category_id>/edit/', methods = ['GET', 'POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedCategory = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
		if request.form['name']:
			editedCategory.name = request.form['name']
		session.add(editedCategory)
		session.commit()
		flash("Category Edited!")
		return redirect(url_for('listCategories'))
    else:
		return render_template('editCategory.html', category_id = category_id, editedCategory = editedCategory)

@app.route('/catsupplies/<int:category_id>/delete', methods = ['GET', 'POST'])
def deleteCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    deletedCategory = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
		session.delete(deletedCategory)
		session.commit()
		flash("Category Deleted!")
		return redirect(url_for('listCategories'))
    else:
		return render_template('deleteCategory.html', category_id = category_id, deletedCategory = deletedCategory)


@app.route('/catsupplies/<int:category_id>/')
def listSupplyItems(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(SupplyItem).filter_by(category_id=category.id)

    return render_template('item.html', category = category, items = items)


@app.route('/catsupplies/<int:category_id>/new/', methods = ['GET', 'POST'])
def newSupplyItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
		newItem = SupplyItem(name = request.form['name'], brand = "brand", price = "$"+request.form['price'], category_id = category_id)
		session.add(newItem)
		session.commit()
		flash("New item created!")
		return redirect(url_for('listSupplyItems', category_id = category_id))
    else:
		return render_template('newSupplyItem.html', category_id = category_id)


@app.route('/catsupplies/<int:category_id>/<int:item_id>/edit', methods = ['GET', 'POST'])
def editSupplyItem(category_id, item_id):
    if 'username' not in login_sesion:
        return redirect('/login')
    editedItem = session.query(SupplyItem).filter_by(id = item_id).one()
    if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
		if request.form['ingredients']:
			editedItem.ingredients = request.form['ingredients']
		if request.form['price']:
			editedItem.price = request.form['price']
		session.add(editedItem)
		session.commit()
		flash("Item Edited!")
		return redirect(url_for('listSupplyItems', category_id = category_id))
    else:
		return render_template('editSupplyItem.html', category_id = category_id, item_id = item_id, item = editedItem )


@app.route('/catsupplies/<int:category_id>/<int:item_id>/delete/', methods = ['GET', 'POST'])
def deleteSupplyItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    deletedItem = session.query(SupplyItem).filter_by(id = item_id).one()
    if request.method == 'POST':
		session.delete(deletedItem)
		session.commit()
		flash("Item Deleted!")
		return redirect(url_for('listSupplyItems', category_id = category_id))
    else:
		return render_template('deleteSupplyItem.html', category_id = category_id, item_id = item_id, deletedItem = deletedItem)


# ADD JSON API ENDPOINT

@app.route('/catsupplies/items/JSON')
def allItemsJSON():
	items = session.query(SupplyItem).all()
	return jsonify(SupplyItems = [i.serialize for i in items])
	
@app.route('/catsupplies/<int:category_id>/items/JSON')
def supplyItemJSON(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(SupplyItem).filter_by(
        category_id = category_id).all()
    return jsonify(SupplyItems = [i.serialize for i in items])


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)
