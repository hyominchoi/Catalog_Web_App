from flask import Flask, render_template, redirect, url_for, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, SupplyItem
app = Flask(__name__)

engine = create_engine('sqlite:///catsupplies.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catsupplies/')
def listCategories():
	return "List of categories"

@app.route('/catsupplies/new/')
def newCategory():
	return "Create a new category"

@app.route('/catsupplies/edit/')
def editCategory(category_id):
	return "Edit an existing category"

@app.route('/catsupplies/delete')
def deleteCateogry(category_id):
	return "Delete an existing category"

@app.route('/catsupplies/<int:category_id>/')
def listSupplyItems(category_id):
    return "List supply items of a category"

@app.route('/catsupplies/<int:category_id>/new/')
def newSupplyItem(category_id):
	return "Create a new supply item"

@app.route('/catsupplies/<int:category_id>/<int:item_id>/edit/')
def editSupplyItem(category_id, item_id):
	return "Edit an existing supply item"

@app.route('/catsupplies/<int:category_id>/<int:item_id>/delete/')
def deleteSupplyItem(category_id, item_id):
	return "Delete an existing supply item"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
