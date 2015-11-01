from flask import Flask, render_template, redirect, url_for, request, jsonify
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
	categories = session.query(Category).all()

	return render_template('categories.html', categories = categories)


@app.route('/catsupplies/new/', methods = ['GET', 'POST'])
def newCategory():
	if request.method == 'POST':
		if request.form['name']:
			newCategory = Category(name = request.form['name'])
			session.add(newCategory)
			session.commit()
			return redirect(url_for('listCategories'))
	else:	
		return render_template('newCategory.html')


@app.route('/catsupplies/<int:category_id>/edit/', methods = ['GET', 'POST'])
def editCategory(category_id):
	editedCategory = session.query(Category).filter_by(id = category_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editedCategory.name = request.form['name']
		session.add(editedCategory)
		session.commit()
		return redirect(url_for('listCategories'))
	else:
		return render_template('editCategory.html', category_id = category_id, editedCategory = editedCategory)

@app.route('/catsupplies/<int:category_id>/delete', methods = ['GET', 'POST'])
def deleteCategory(category_id):
	deletedCategory = session.query(Category).filter_by(id = category_id).one()
	if request.method == 'POST':
		session.delete(deletedCategory)
		session.commit()
		return redirect(url_for('listCategories'))

	else:
		return render_template('deleteCategory.html', category_id = category_id, deletedCategory = deletedCategory)


@app.route('/catsupplies/<int:category_id>/')
def listSupplyItems(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(SupplyItem).filter_by(category_id=category.id)

    return render_template('item.html', category = category, items = items)


@app.route('/catsupplies/<int:category_id>/new/', methods = ['GET', 'POST'])
def newSupplyItem(category_id):
	if request.method == 'POST':
		newItem = SupplyItem(name = request.form['name'], brand = "brand", price = "$"+request.form['price'], category_id = category_id)
		session.add(newItem)
		session.commit()
		return redirect(url_for('listSupplyItems', category_id = category_id))
	else:
		return render_template('newSupplyItem.html', category_id = category_id)


@app.route('/catsupplies/<int:category_id>/<int:item_id>/edit', methods = ['GET', 'POST'])
def editSupplyItem(category_id, item_id):
	editedItem = session.query(SupplyItem).filter_by(id = item_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
		if request.form['ingredients']:
			editedItem.ingredients = request.form['ingredients']
		if request.form['price']:
			editedItem.price = request.form['price']
		session.add(editedItem)
		session.commit()
		return redirect(url_for('listSupplyItems', category_id = category_id))
	else:
		return render_template('editSupplyItem.html', category_id = category_id, item_id = item_id, item = editedItem )


@app.route('/catsupplies/<int:category_id>/<int:item_id>/delete/', methods = ['GET', 'POST'])
def deleteSupplyItem(category_id, item_id):
	deletedItem = session.query(SupplyItem).filter_by(id = item_id).one()
	if request.method == 'POST':
		session.delete(deletedItem)
		session.commit()
		return redirect(url_for('listSupplyItems', category_id = category_id))
	else:
		return render_template('deleteSupplyItem.html', category_id = category_id, item_id = item_id, deletedItem = deletedItem)


# ADD JSON API ENDPOINT

@app.route('/catsupplies/items/JSON')
def allItemsJSON():
	items = session.query(SupplyItem).all()
	return jsonify(SupplyItems = [i.serialize for i in items])
	
@app.route('/catsupplies/<int:category_id>/items/JSON')
def supplyItemJSON(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(SupplyItem).filter_by(
        category_id = category_id).all()
    return jsonify(SupplyItems = [i.serialize for i in items])


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
