#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, url_for, flash
from flask import jsonify, make_response, request, redirect
from flask import session as login_session
from flask_wtf.csrf import CSRFProtect, CSRFError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from werkzeug.utils import secure_filename
import crud
import random
import string
import json
import httplib2
import requests
import os

# Protect application from third party attack
csrf = CSRFProtect()


UPLOAD_FOLDER = './static/uploads'
# Extensions that are allowed to upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 2MB is the largest size of upload file
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
csrf.init_app(app)

CLIENT_ID = json.loads(
    open('g_client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Vóisa Recipes"


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Log in using Facebook API
@csrf.exempt
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    # Exchange client token for long-lived server-side token
    app_id = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/v2.8/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s') % (app_id, app_secret, access_token)
    http = httplib2.Http()
    result = http.request(url, 'GET')[1]
    data = json.loads(result)

    # Extract the access token from response
    token = 'access_token=' + data['access_token']

    # Use token to get user info from API.
    url = 'https://graph.facebook.com/v2.8/me?%s&fields=name,id,email' % token
    http = httplib2.Http()
    result = http.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['api_id'] = data["id"]

    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = ("https://graph.facebook.com/v2.8/me/"
           "picture?{}&redirect=0&height=200&width=200".format(token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]

    # See if user exists
    user_id = crud.getUserID(login_session['email'])
    if not user_id:
        user_id = crud.createUser(login_session)
    login_session['user_id'] = user_id

    flash("Now logged in as %s" % login_session['username'])
    return 'Logged in'


# Log in using Google API
@csrf.exempt
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
        oauth_flow = flow_from_clientsecrets('g_client_secrets.json', scope='')
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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps("Current user is already"
                                            " connected"), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['api_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = crud.getUserID(data["email"])
    if not user_id:
        user_id = crud.createUser(login_session)
    login_session['user_id'] = user_id

    flash("you are now logged in as %s" % login_session['username'])
    return 'Logged in'


# To log out user
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        elif login_session['provider'] == 'facebook':
            fbdisconnect()
        print login_session
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


# Provide all recipes as a JSON endpoint
@app.route('/catalog.json')
def JSONcatalog():
    items = crud.findAllItems()
    return jsonify(item=[r.serialize for r in items])


# Home page of web app
@app.route('/')
@app.route('/catalog')
def showCategories():
    # To list all recipes' categories
    categories = crud.findAllCategory()
    # To list 10 recent items that were added
    items = crud.findRecentItems()
    if 'username' not in login_session:
        return render_template('catalog.html', categories=categories,
                               items=items)
    else:
        log = login_session
        return render_template('catalog.html', categories=categories,
                               items=items, log=log)


# To create a category
@app.route('/catalog/category/create', methods=['GET', 'POST'])
def createCategory():
    if 'username' not in login_session:
            flash('You are not logged in')
            return redirect(url_for('showCategories'))
    else:
        user_id = crud.getUserID(login_session['email'])
        user = crud.getUserInfo(user_id)
        log = True
        if request.method == 'POST':
            new_category_name = request.form['name']
            crud_function = crud.newCategory(new_category_name)
            if crud_function:
                return render_template('newcategory.html',
                                       error=crud_function, log=log)
            else:
                flash('Category has been created')
                return redirect(url_for('showCategories'))
        else:
            return render_template('newcategory.html', log=log)


# Show all recipes by a specific category
@app.route('/catalog/<string:category_name>/items')
def showItems(category_name):
    categories = crud.findAllCategory()
    # Find items by category
    itemsByCategory = crud.findItems_byCategory(category_name)
    if 'username' not in login_session:
        return render_template('itemsbycategory.html', categories=categories,
                               items=itemsByCategory,
                               category_name=category_name)
    else:
        log = login_session
        return render_template('itemsbycategory.html', categories=categories,
                               items=itemsByCategory, log=log,
                               category_name=category_name)


# Show a specific recipe
@app.route('/catalog/<string:category_name>/<string:item_name>')
def showItem(category_name, item_name):
    # Find the recipe requested
    item = crud.findItem(item_name)
    category = crud.findCategory(category_name)
    if item is None or category is None:
            flash('This item does not exist')
            return redirect(url_for('showCategories'))
    else:
        ingredients = crud.findIngredients(item.id)
        if 'username' not in login_session:
            return render_template('item.html', item=item,
                                   ingredients=ingredients)
        else:
            log = login_session
            if item.user_id == login_session['user_id']:
                own_user = True
                return render_template('item.html', log=log, own_user=own_user,
                                       ingredients=ingredients, item=item)
            else:
                return render_template('item.html', item=item, log=log,
                                       ingredients=ingredients)


# Check if file upload is a type allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Create a new recipe
@app.route('/catalog/item/create', methods=['GET', 'POST'])
def createItem():
    if 'username' not in login_session:
        flash('You must be logged to create a item')
        return redirect(url_for('showCategories'))
    else:
        log = login_session
        categories = crud.findAllCategory()
        if request.method == 'POST':
            name = request.form['name']
            directions = request.form['directions']
            ingredient1 = request.form['ingredient1']
            ingredient2 = request.form['ingredient2']
            ingredient3 = request.form['ingredient3']
            ingredient4 = request.form['ingredient4']
            ingredient5 = request.form['ingredient5']
            category_id = request.form.get('category')
            image = request.files['file']
            # Get user from login_session
            user_id = login_session['user_id']

            have_error = False
            params = {}
            params['name'] = name
            params['directions'] = directions
            params['ingredient1'] = ingredient1
            params['ingredient2'] = ingredient2
            params['ingredient3'] = ingredient3
            params['ingredient4'] = ingredient4
            params['ingredient5'] = ingredient5

            ingredients = [ingredient1, ingredient2, ingredient3, ingredient4,
                           ingredient5]

            if not name:
                have_error = True
                params['error_name'] = "You must write a name"

            if not directions:
                have_error = True
                params['error_directions'] = "You must write directions"

            if ingredients.count(u'') == 5:
                have_error = True
                params['error_ingredients'] = "At least one ingredient is" \
                                              " required"

            if category_id is None:
                have_error = True
                params['error_category'] = "You must choose a category"

            have_file = False
            if image:
                if allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                            filename))
                    file_url = os.path.join(app.config['UPLOAD_FOLDER'],
                                            filename)[1:]
                    have_file = True
                else:
                    have_error = True
                    params['error_file'] = "You must select .png, .jpg or" \
                                           " .jpeg file"

            if have_error:
                return render_template('newitem.html', categories=categories,
                                       log=log, **params)

            if have_file:
                crud_function = crud.newItem(name, directions, ingredients,
                                             int(category_id), user_id,
                                             filename, file_url)
            else:
                crud_function = crud.newItem(name, directions, ingredients,
                                             int(category_id), user_id)

            if crud_function:
                return render_template('newitem.html', error=crud_function,
                                       categories=categories, log=log,
                                       **params)
            else:
                flash('Item has been created')
                category = crud.findCategory_byID(category_id)
                return redirect(url_for('showItems',
                                        category_name=category.name))
        else:
            return render_template('newitem.html', categories=categories,
                                   log=log)


# Edit a recipe
@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def editItem(item_name):
    if 'username' not in login_session:
        flash('You must be logged to edit a item')
        return redirect(url_for('showCategories'))
    else:
        log = login_session
        item = crud.findItem(item_name)
        if request.method == 'POST':
            # Only the user that created can edit
            if item.user_id == login_session['user_id']:
                original_name = item.name
                categories = crud.findAllCategory()
                item_name = None
                item_directions = None
                item_ingredient1 = None
                item_ingredient2 = None
                item_ingredient3 = None
                item_ingredient4 = None
                item_ingredient5 = None
                item_category_id = None
                item_image = None
                have_edition = False
                have_edition_ingredient = False

                if request.form['name']:
                    have_edition = True
                    item_name = request.form['name']
                if request.form['directions']:
                    have_edition = True
                    item_directions = request.form['directions']
                if request.form['ingredient1']:
                    have_edition_ingredient = True
                    item_ingredient1 = request.form['ingredient1']
                if request.form['ingredient2']:
                    have_edition_ingredient = True
                    item_ingredient2 = request.form['ingredient2']
                if request.form['ingredient3']:
                    have_edition_ingredient = True
                    item_ingredient3 = request.form['ingredient3']
                if request.form['ingredient4']:
                    have_edition_ingredient = True
                    item_ingredient4 = request.form['ingredient4']
                if request.form['ingredient5']:
                    have_edition_ingredient = True
                    item_ingredient5 = request.form['ingredient5']
                if request.form.get('category') is not None:
                    have_edition = True
                    item_category_id = int(request.form.get('category'))
                if request.files['file']:
                    have_edition = True
                    item_image = request.files['file']

                if have_edition_ingredient:
                    ingredients = []
                    ingredients.append(item_ingredient1)
                    ingredients.append(item_ingredient2)
                    ingredients.append(item_ingredient3)
                    ingredients.append(item_ingredient4)
                    ingredients.append(item_ingredient5)

                have_file = False
                if item_image:
                    if allowed_file(image.filename):
                        os.remove(os.path.join(
                                            app.config['UPLOAD_FOLDER'],
                                            item.image_filename))
                        filename = secure_filename(item_image.filename)
                        item_image.save(
                                    os.path.join(app.config['UPLOAD_FOLDER'],
                                                 filename))
                        file_url = os.path.join(app.config['UPLOAD_FOLDER'],
                                                filename)[1:]
                    else:
                        flash("Your image wasn't edited because it must be "
                              ".png, .jpg or .jpeg file")
                        filename = None
                        file_url = None

                    crud.editItem(original_name, item_name, item_directions,
                                  ingredients, item_category_id, filename,
                                  file_url)
                    category = crud.findCategory_byID(item_category_id)
                    flash('Your item has been edited')
                    return redirect(url_for('showItem', item_name=item.name,
                                            category_name=item.category.name))
                elif have_edition:
                    ingredients = None
                    crud.editItem(original_name, item_name, item_directions,
                                  ingredients, item_category_id, filename=None,
                                  file_url=None)
                    category = crud.findCategory_byID(item_category_id)
                    flash('Your item has been edited')
                    return redirect(url_for('showItem', item_name=item.name,
                                            category_name=item.category.name))
                else:
                    flash('You did not change anything')
                    return render_template('edititem.html', item=item)
            else:
                flash('You can not edit a item by other use')
                return redirect(url_for('showCategories'))
        else:
            if item is None:
                flash("This item does not exist")
                return redirect(url_for('showCategories'))
            else:
                ingredients = crud.findIngredients(item.id)
                count = 1
                list_ingredients = []
                for ingredient in ingredients:
                    list_ingredients.append(['ingredient'+str(count),
                                             ingredient.ingredient_name])
                    count += 1
                while count <= 5:
                    list_ingredients.append(['ingredient'+str(count), ''])
                    count += 1
                categories = crud.findAllCategory()
                return render_template('edititem.html', item=item,
                                       ingredients=list_ingredients,
                                       categories=categories, log=log)


# Delete a recipe
@app.route('/catalog/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(item_name):
    if 'username' not in login_session:
        flash('You must be logged to delete a item')
        return redirect(url_for('showCategories'))
    else:
        log = login_session
        item = crud.findItem(item_name)
        if request.method == 'POST':
            # Only the user that created can delete
            if item.user_id == login_session['user_id']:
                if item.image_filename:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'],
                                           item.image_filename))
                crud.deleteItem(item_name)
                flash('This item has been deleted')
                return redirect(url_for('showCategories'))
            else:
                flash('You can not delete item by other user')
                return redirect(url_for('showCategories'))
        else:
            if item is None:
                flash('This item does not exist')
                return redirect(url_for('showCategories'))
            else:
                return render_template('deleteitem.html', item=item, log=log)


# Empty login_session if provides is Facebook
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['api_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = ('https://graph.facebook.com/{}/'
           'permissions?access_token={}'.format(facebook_id, access_token))
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['access_token']
    del login_session['api_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['provider']
    del login_session['state']
    return "you have been logged out"


# Empty login_session if provides is Google
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    del login_session['access_token']
    del login_session['api_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['provider']
    del login_session['state']
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for'
                                            'given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Handle a CSRF error that may occur
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400


# The maximum file size to upload is 2MB,
# larger files generate error 413 and are handled by this route
@app.errorhandler(413)
def request_entity_too_large(error):
    flash('Too large')
    return redirect(url_for('showCategories'))

if __name__ == '__main__':
    app.secret_key = '^4u!gn!3Y8Fv'
    app.wtf_csrf_secret_key = 'aj@2lL!OA0NU'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
