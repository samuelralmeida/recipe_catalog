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
