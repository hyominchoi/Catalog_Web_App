## This file was modified from the original version provided by Udacity
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class SupplyItem(Base):
    __tablename__ = 'supply_item'

    name = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True)
    brand = Columns(String(30), nullable=False)
    price = Column(String(8), nullable=False)
    grain_free = Column(Boolean)
    ingredients = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)


engine = create_engine('sqlite:///catsupplies.db')


Base.metadata.create_all(engine)
