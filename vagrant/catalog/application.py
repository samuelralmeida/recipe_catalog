#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, url_for, flash, request, redirect
from flask import session as login_session
import crud
import json
import facebook_login
import random
import string

app = Flask(__name__)

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={}&client_secret={}&fb_exchange_token={}'.format(
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.10/me"
    # strip expire tag from access token
    token = result.split('&')[0]

    url = 'https://graph.facebook.com/v2.10/me?{}&fields=name,id,email'.format(token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print "url sent for api access: {}".format(url)
    print "API JSON result: {}".format(result)
    data = json.loads(result)
    #login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # Get user picture
    url = 'https://graph.facebook.com/v2.10/me/picture?{}&redirect=0&height=200&width=200'.format(
        token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    user_id = crud.getUserID(login_session['email'])
    if not user_id:
        user_id = crud.createUser(login_session)
    login_session['user_id'] = user_id

    return redirect(url_for('showCategories'))

"""@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    response = facebook_login.fbconnect(login_session, access_token)
    if response == "Logged in":
        flash("Now logged in as %s" % login_session['username'])
        return redirect(url_for('showCategories'))
    return response
"""
@app.route('/catalog.json')
def JSONcatalog():
    return "JSON de todo o catálogo"

@app.route('/')
@app.route('/catalog')
def showCategories():
    categories = crud.findAllCategory()
    if 'username' not in login_session:
        return render_template('catalog.html', categories=categories)
    else:
        log = True
        return render_template('catalog.html', categories=categories, log=log)

#this route only can be access for adim at the end of the app
@app.route('/catalog/category/create', methods=['GET', 'POST'])
def createCategory():
    if request.method == 'POST':
        new_category_name = request.form['name']
        crud_function = crud.newCategory(new_category_name)
        if crud_function:
            return render_template('newcategory.html', error=crud_function)
        else:
            flash('Category has been created')
            return redirect(url_for('showCategories'))
    else:
        return render_template('newcategory.html')

@app.route('/catalog/<string:category_name>/items')
def showItems(category_name):
    return "show all items of category"

@app.route('/catalog/<string:category_name>/<string:item_name>')
def showItem(category_name, item_name):
    return "show item was chose"

@app.route('/catalog/item/create', methods=['GET', 'POST'])
def createItem():
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
        # carregar usuário automaticamente de login_session
        # user_id = login_session['user_id']

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
            params['error_description'] = "You must write a description"

        if ingredients is False:
            have_error = True
            params['error_ingredients'] = "At least one ingredient is required"

        if category_id is None:
            have_error = True
            params['error_category'] = "You must choose a category"

        if have_error:
            return render_template('newitem.html',
                                   categories=categories, **params)

        crud_function = crud.newItem(name, directions, ingredients,
                        int(category_id), user_id=0)
        if crud_function:
            return render_template('newitem.html', error=crud_function,
                                   categories=categories, **params)
        else:
            flash('Item has been created')
            category = crud.findCategory_byID(category_id)
            return redirect(url_for('showItems', category_name=category.name))
    else:
        return render_template('newitem.html', categories=categories)
    return "create a item"

@app.route('/catalog/<string:item_name>/edit')
def editItem(item_name):
    return "edit item was chose"

@app.route('/catalog/<string:item_name>/delete')
def deleteItem(item_name):
    return "delete item was chose"

if __name__ == '__main__':
    app.secret_key = '^4u!gn!3Y8Fv'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
