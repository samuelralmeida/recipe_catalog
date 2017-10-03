#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(80), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
        }


class Ingredient(Base):
    __tablename__ = 'ingredient'

    id = Column(Integer, primary_key=True)
    ingredient_name = Column(String(80), nullable=False)
    ingredient_measure = Column(String(80), nullable=False)

    @property
    def serialize(self):
        return {
            'ingredient_name': self.ingredient_name,
            'ingredient_measure': self.ingredient_measure,
            'id': self.id,
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('ingredient.id'))
    ingredient = relationship(Ingredient)
    directions = Column(String(500))
    link = Column(String(250))
    picture = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'category': self.category,
            'ingredient': self.ingredient,
            'description': self.description,
            'link': self.link,
            'picture': self.picture,
            'user_id': self.user_id,
        }


engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
