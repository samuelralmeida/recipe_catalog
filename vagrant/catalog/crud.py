#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item, Ingredient, engine
from sqlalchemy import desc

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def findAllCategory():
    return session.query(Category).all()

def findCategory(name):
    return session.query(Category).filter_by(name=name).first()

def findCategory_byID(category_id):
    return session.query(Category).filter_by(id=category_id).first()

def findRecentItems():
    return session.query(Item).order_by(desc(Item.time_created)).limit(10)

def newCategory(name):
    result = findCategory(name)
    if result:
        error = "A category with that name already exists"
        return error
    else:
        new_category = Category(name=name)
        session.add(new_category)
        session.commit()
        return None

def findItem(name):
    return session.query(Item).filter_by(name=name).first()

def findIngredients(item_id):
    return session.query(Ingredient).filter_by(item_id=item_id).all()

def findItemID(name):
    item = session.query(Item).filter_by(name=name).one()
    return item.id

def findItems_byCategory(category):
    result = findCategory(category)
    if not result:
        return None
    _id = result.id
    return session.query(Item).filter_by(category_id=_id).all()

def addIngredients(ingredients, item_id):
    for ingredient in ingredients:
        if ingredient:
            new_ingredient = Ingredient(ingredient_name=ingredient,
                                      item_id=item_id)

def newItem(name, directions, ingredients, category_id, user_id):
    result = findItem(name)
    if result:
        error = "A item with that name already exists"
        return error
    else:
        new_item = Item(name=name, directions=directions,
                        category_id=category_id, user_id=user_id)
        session.add(new_item)
        session.commit()
        item_id = findItemID(name)
        addIngredients(ingredients,item_id)
        return None

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'],
                    picture=login_session['picture'],
                    api_id=login_session['api_id'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

def deleteItem(item_name):
    item = findItem(item_name)
    if item:
        session.delete(item)
        session.commit()

def editAdmin(email):
    user_id = getUserID(email)
    user = getUserInfo(user_id)
    user.group = 'admin'
    session.add(user)
    session.commit()

def deleteUser(email):
    user_id = getUserID(email)
    user = getUserInfo(user_id)
    session.delete(user)
    session.commit()
