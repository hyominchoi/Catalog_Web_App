# The original version of the script was provided by Udacity
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, SupplyItem

engine = create_engine('sqlite:///catsupplies.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

category1 = Category(name="Wet Food")

session.add(category1)
session.commit()

category2 = Category(name="Treats")

session.add(category2)
session.commit()

category3 = Category(name="Supplements")

session.add(category3)
session.commit()

item1 = SupplyItem(name="Beef Liver Munchies", brand="Primal", price="$5",
				   grain_free=True, ingredients="beef liver", category=category2)

session.add(item1)
session.commit()

item2 = SupplyItem(name="Hairball Relief", brand="Vet's Best", price="$5.5",
				   grain_free=True, ingredients="yeast, papaya, slippery elm bark",
				   category=category3)

session.add(item2)
session.commit()

item3 = SupplyItem(name="Nu-Cat", brand="VetriScience", price="$13", 
				   ingredients="cehydrated beef liver, taurine, green mussel", 
				   category=category3)

session.add(item3)
session.commit()

item4 = SupplyItem(name="Cat Man Doo Chiken", brand="Cat Man Doo", price="$14",
				   grain_free=True, ingredients="dehydrated chicken breast",
				   category=category2)

session.add(item4)
session.commit()

item5 = SupplyItem(name="Puka Luau Succulent Chicken in Chicken Consomme Canned Cat Food",
				   brand="Tiki Cat", ingredients="Chicken 62%, Chicken Consomme 34%",
				   price="$20",category=category1)

session.add(item5)
session.commit()


print "added items!"


