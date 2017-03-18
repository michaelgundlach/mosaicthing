from google.appengine.ext import webapp

class NotFound(webapp.RequestHandler):
    def post(self):
        get(self)

    def get(self):
        self.response.out.write("""
            <html><head>
            <link type="text/css" rel="stylesheet"
             href="/static/style.css" />
            </head><body>
            <h1>404 Not Found</h1>
            The requested URL<br>%s<br>was not found on this server.
            </body></html>
            """ % self.request.uri)
