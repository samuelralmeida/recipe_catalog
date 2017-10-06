#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item, Ingredient, engine

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def findAllCategory():
    return session.query(Category).all()

def findCategory(name):
    return session.query(Category).filter_by(name=name).first()

def findCategory_byID(category_id):
    return session.query(Category).filter_by(id=category_id).first()

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

def findItemID(name):
    item = session.query(Item).filter_by(name=name).one()
    return item.id

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
