Project: Catalog Building, Web Application  - [Hyomin Choi]
===============================================================
* This project is suggested and guided by Udacity: We develop a RESTful web application using the Python framework Flask along with implementing third-party OAuth authentication. We will then learn when to properly use the various HTTP methods available to you and how these methods relate to CRUD (create, read, update and delete) operations.

* This catalog stores information about cat supply items using two dataframes in the backbone. Users can create, read, update and delete supply categories and single items as well.


Required Libraries and Dependencies
-----------------------------------
* This project is mostly written in Python v2.* on Vagrant Virtual Machine environment. To run the virtual machine, we download Virtual Box and type "vagrant up" and "vagrant ssh" in the terminal.
* The database is set up by database-setup.py and then managed by SQLite and SQLAlchemylibrary. 
* The webpages were written using Flask Frameworks.


How to Run Project
------------------
* First, execute python database_setup.py to initialize the database.  
* To run local sever, execute python final_project.py and then access to "localhost:{port}/catsupplies" on your web browser. The port number can be found on final_project.py.  


Miscellaneous
-------------
* Next goa: I want to add web-scrapping functionality to record the lowest possible prices from various websites.

