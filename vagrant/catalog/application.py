#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, url_for, flash, request, redirect
import crud

app = Flask(__name__)

@app.route('/login')
def showLogin():
    return "show login page"

@app.route('/catalog.json')
def JSONcatalog():
    return "JSON de todo o catálogo"

@app.route('/')
@app.route('/catalog')
def showCategories():
    categories = crud.findAllCategory()
    return render_template('catalog.html', categories=categories)

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
    app.run(host='0.0.0.0', port=8000)
