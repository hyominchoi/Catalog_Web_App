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
@app.route('/catsupplies/<int:category_id>/')
def supplyItem(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(SupplyItem).filter_by(category_id=category.id)

    return render_template('item.html', category = category, items = items)

@app.route('/catsupplies/<int:category_id>/<int:item_id>/edit/')
def editSupplyItem(category_id, item_id):
	return "page to edit a supply item from a certain category"

@app.route('/catsupplies/<int:category_id>/<int:item_id>/delete/')
def deleteSupplyItem(category_id, item_id):
	return "page to delete a supply item from a certain category"


@app.route('/catsupplies/<int:category_id>/new/', methods = ['GET', 'POST'])
def newSupplyItem(category_id):
	return "page to create a supply item of a certain category"
	#if request.method == 'POST':
	#	newItem = SupplyItem(name = request.form['name'], category_id = category_id)
	#	session.add(newItem)
	#	session.commit()
	#	return redirect(url_for('catsupplies', category_id = category_id))
	#else:
	#	return render_template('newSupplyItem.html', category_id = category_id)





if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)