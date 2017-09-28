#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item, engine

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def findAllCategory():
    return session.query(Category).all()

def findCategory(name):
    return session.query(Category).filter_by(name=name).first()

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
