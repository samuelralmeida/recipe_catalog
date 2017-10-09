#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(80), nullable=False)
    picture = Column(String(250))
    api_id = Column(String(250))
    group = Column(String(5), default='user')


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    item = relationship("Item", backref="category")

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'item': self.item,
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    directions = Column(String(500))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    category_id = Column(Integer, ForeignKey('category.id'))
    ingredient = relationship("Ingredient", backref='item')
    time_created = Column(DATETIME(timezone=True), server_default=func.now())
    time_updated = Column(DATETIME(timezone=True), onupdate=func.now())

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""

        def listOfIngredients(ingredients):
            list_ingredients = []
            for i in ingredients:
                list_ingredients.append(i.ingredient_name)
            return list_ingredients

        return {
            'name': self.name,
            'id': self.id,
            'category': self.category.name,
            'directions': self.directions,
            'ingredients': listOfIngredients(self.ingredient)
        }


class Ingredient(Base):
    __tablename__ = 'ingredient'

    id = Column(Integer, primary_key=True)
    ingredient_name = Column(String(80), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'))

    @property
    def serialize(self):
        return {
            'ingredient_name': self.ingredient_name,
            'item_id': self.item_id,
            'id': self.id,
            'item': self.item.name,
        }


engine = create_engine('sqlite:///recipes.db')

Base.metadata.create_all(engine)
