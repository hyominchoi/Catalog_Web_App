from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, SupplyItem


engine = create_engine('sqlite:///catsupplies.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/catsupplies"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                message = ""
                message += "<body><html>"
                # Get the list of categories
                for line in session.query(Category).all():
                    message += line.name + "<br>"
                    message += "<a href = '/edit'> edit </a><br>"
                    message += "<a href = '/delete'> delete </a><br>"
                # Create new category link
                message += "<br><br><a href = '/new_category'> Make a new Category </a>"
                message += "</body></html>"
                self.wfile.write(message)
                return


            if self.path.endswith("/new_category"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                message = ""
                message += "<html><body>"
                message += "<h1> Make a new category </h1>"
                message += "<form method= 'POST' enctype = 'multipart/form-data' action = '/new_category'>"
                message += "<input name = 'newCategoryName' type = 'text' placeholder = 'New Category Name' >"
                message += "<input type = 'submit' value = 'Create'>"
                message += "<br><a href = '/catsupplies'> Go back </a>"
                message += "</form></body></html>"
                self.wfile.write(message)
                return 

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)
        

    # do_POST function displays a new message after a user enters new data
    def do_POST(self):
        try:
            
            if self.path.endswith("/new_category"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newCategoryName')

                    # Create new Category Object
                    newCategory = Category(name=messagecontent[0])
                    session.add(newCategory)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/catsupplies')
                    self.end_headers()


        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
