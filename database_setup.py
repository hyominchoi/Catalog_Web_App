## This file was modified from the original version provided by Udacity
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", cascade="save-update")

    @property
    def serialize(self):
        """ Return object data in easily serialize format """
        return {
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id,
        }


class SupplyItem(Base):
    __tablename__ = 'supply_item'

    name = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True)
    brand = Column(String(30), nullable=False)
    price = Column(String(8), nullable=False)
    grain_free = Column(Boolean)
    ingredients = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(
        "Category", 
        backref=backref("items", cascade="all, delete-orphan")
        )
    image_url = Column(String(300))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


# Add serialize function to be able to send JSON objects in a
# serializable format

    @property
    def serialize(self):
        """ Return object data in easily serialize format """
        return {
            'name': self.name,
            'ingredients': self.ingredients,
            'id': self.id,
            'price': self.price,
            'brand': self.brand,
            'gran_free': self.grain_free,
            'user_id': self.user_id,
        }

engine = create_engine('sqlite:///catsupplies.db')


Base.metadata.create_all(engine)

