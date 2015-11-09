# IMPORTS FOR FLASK FRAME WORKS
from flask import Flask, render_template, redirect, url_for, request, flash
# IMPORTS FOR API ENDPOINTS
from flask import jsonify
import xml.etree.ElementTree as ET
# IMPORTS FOR DATABASE
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, SupplyItem, User
# IMPORTS FOR LOGIN
from flask import session as login_session
import random
import string
# IMPORTS FOR LOGIN -- GCONNECT FUNCTION
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
# IMPORTS FOR DECORATOR
from functools import wraps

app = Flask(__name__)

# READ AND SAVE CLIENT_ID FOR GOOGLE PLUS LOGIN FUNCTIONALITY
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Cat Supplies Catalog App"


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    """
    This function creates random string for login, state token.
    The variable is stored in login_session dictionary.

    """

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """ 
    This function enables a google plus login by a user.
    More specifically, it validates all the credentials and
    if everything is validated then proceed to successful login.

    """

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
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if user exists, if not then create a new user account
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


def createUser(login_session):
    """
    This creates a new user account given a login_session dictionary.
    The new user account is saved in User table in the db.
    Returns user.id, a primary key assgined in User table in the db.
    """

    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """
    Given a user_id, returns entire user info from the database
    Input: user_id integer
    Output: user object from the database
    """
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """
    Give an email, returns user.id found in the database
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    """
    This function enables a user to logout from the web app.
    After logout, the user is redirected to the main page
    and will see a flash message.
    """
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials

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
        del login_session['user_id']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("logged out")
        return redirect(url_for('listCategories'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        flash("log out failed")
        return redirect(url_for('listCategories'))


# DECORATOR FUNCTION FOR LOGIN REQUIREMENT. REDIRECT TO LOGIN PAGE
def login_required(f):
    """
    Decorator function -- check login status and redirect to login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in login_session:
            return redirect(url_for('showLogin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# CONNECT TO THE DATABASE - catsupplies
engine = create_engine('sqlite:///catsupplies.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# FLASK FRAMEWORKS -- CREATING WEB PAGES
@app.route('/')
# MAIN PAGE GENERATOR -- SHOWS CATEGORIES OF SUPPLIES
@app.route('/catsupplies/')
def listCategories():
    """
    This function generates the main page, '/catsupplies'.
    The main page contains login/out buttons.
    """
    categories = session.query(Category).all()
    if 'user_id' not in login_session:
        return render_template('public_categories.html', categories=categories,
                               login_session=login_session)
    else:
        return render_template('categories.html', categories=categories,
                               login_session=login_session)


# PAGE FOR CREATING A NEW CATEGORY. REQUIRES LOGIN
@app.route('/catsupplies/new/', methods=['GET', 'POST'])
@login_required
def newCategory():
    """
    This function lets a logged-in user generate a new category and saves to
    the database catsupplies.db.
    """

    if request.method == 'POST':
        if request.form['name']:
            newCategory = Category(name=request.form['name'],
                                   user_id=login_session['user_id'])
            session.add(newCategory)
            session.commit()
            flash("New category created!")
            return redirect(url_for('listCategories'))
    else:
        return render_template('newCategory.html')


# PAGE FOR EDITING AN EXISTING CATEGORY CREATED BY THE LOGGED IN USER.
@app.route('/catsupplies/<int:category_id>/edit/', methods=['GET', 'POST'])
@login_required
def editCategory(category_id):
    """
    This function lets a logged-in user edit an existing category and
    saves changes to the database catsupplies.db.
    """
    editedCategory = session.query(Category).get(category_id)
    if editedCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this categroy. Please create your own category in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        session.add(editedCategory)
        session.commit()
        flash("Category Edited!")
        return redirect(url_for('listCategories'))
    else:
        return render_template(
            'editCategory.html',
            category_id=category_id,
            editedCategory=editedCategory
            )


# PAGE FOR DELETING AN EXISTING CATEGORY. REQUIRES LOGIN
@app.route('/catsupplies/<int:category_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_id):
    """
    This function lets a logged-in user delete an existing category and
    saves changes to the database catsupplies.db.
    """
    deletedCategory = session.query(Category).get(category_id)
    if deletedCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this category. Please create your own category in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(deletedCategory)
        session.commit()
        flash("Category Deleted!")
        return redirect(url_for('listCategories'))
    else:
        return render_template(
            'deleteCategory.html',
            category_id=category_id,
            deletedCategory=deletedCategory
            )


# GENERATING PAGE FOR EACH CATEGORY -- LIST ALL THE SUPPLY ITEMS
@app.route('/catsupplies/<int:category_id>/')
def listSupplyItems(category_id):
    """
    This function lists all the supply items saved in catsupplies.db
    given a category_id on the page "item.html".
    """
    category = session.query(Category).get(category_id)
    creator = getUserInfo(category.user_id)
    items = session.query(SupplyItem).filter_by(category_id=category.id)
    if 'user_id' not in login_session or creator.id != login_session['user_id']:
        return render_template(
            'public_item.html',
            category=category,
            items=items,
            creator=creator,
            login_session=login_session
            )
    else:
        return render_template(
            'item.html',
            category=category,
            items=items,
            creator=creator,
            login_session=login_session
            )


# PAGE FORE CREATING A NEW SUPPLY ITEM GIVEN A CATEGORY. LOGIN REQUIRED
@app.route('/catsupplies/<int:category_id>/new/', methods=['GET', 'POST'])
@login_required
def newSupplyItem(category_id):
    """
    This function lets a logged-in user create a new item given
    a category and saves changes to the database catsupplies.db.
    Input : category_id
    """
    category = session.query(Category).filter_by(id=category_id).one()
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add supply items to this category. Please create your own category in order to add items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newItem = SupplyItem(
            name=request.form['name'],
            brand="brand",
            price="$"+request.form['price'],
            image_url=request.form['image_url'],
            ingredients=request.form['ingredients'],
            category_id=category_id,
            user_id=category.user_id
            )
        session.add(newItem)
        session.commit()
        flash("New item created!")
        return redirect(url_for('listSupplyItems', category_id=category_id))
    else:
        return render_template('newSupplyItem.html', category_id=category_id)


# PAGE FOR EDITING AN EXISTING SUPPLY ITEM GIVEN A CATEGORY.
# LOGIN REQUIRED
@app.route('/catsupplies/<int:category_id>/<int:item_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editSupplyItem(category_id, item_id):
    """
    This function lets a logged-in user edit an existing item given
    a category and saves changes to the database catsupplies.db.
    Input : category_id and item_id
    """
    category = session.query(Category).get(category_id)
    editedItem = session.query(SupplyItem).get(item_id)
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit supply items to this category.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['ingredients']:
            editedItem.ingredients = request.form['ingredients']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['image_url']:
            editedItem.image_url = request.form['image_url']
        session.add(editedItem)
        session.commit()
        flash("Item Edited!")
        return redirect(url_for('listSupplyItems', category_id=category_id))
    else:
        return render_template(
            'editSupplyItem.html',
            category_id=category_id,
            item_id=item_id,
            item=editedItem
            )


# PAGE FOR DELETING AN EXISTING SUPPLY ITEM GIVEN A CATEGORY.
# LOGIN REQUIRED
@app.route('/catsupplies/<int:category_id>/<int:item_id>/delete/',
           methods=['GET', 'POST'])
@login_required
def deleteSupplyItem(category_id, item_id):
    """
    This function lets a logged-in user delete an existing item given
    a category and saves changes to the database catsupplies.db.
    Input : category_id and item_id
    """
    category = session.query(Category).get(category_id)
    deletedItem = session.query(SupplyItem).get(item_id)
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete supply items to this category.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        flash("Item Deleted!")
        return redirect(url_for('listSupplyItems', category_id=category_id))
    else:
        return render_template(
            'deleteSupplyItem.html',
            category_id=category_id,
            item_id=item_id,
            deletedItem=deletedItem
            )


# ADD JSON API ENDPOINT
@app.route('/catsupplies/items/JSON')
def allItemsJSON():
    items = session.query(SupplyItem).all()
    return jsonify(SupplyItems=[i.serialize for i in items])


@app.route('/catsupplies/<int:category_id>/items/JSON')
def supplyItemJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(SupplyItem).filter_by(
        category_id=category_id).all()
    return jsonify(SupplyItems=[i.serialize for i in items])


# ADD XML API ENDPOINT
@app.route('/catsupplies/items/XML')
def allItemsXML():
    items = session.query(SupplyItem).all()
    return render_template('items.xml',items=items)
    

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
