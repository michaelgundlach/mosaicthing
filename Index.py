from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api import users

from Mosaic import MosaicImage

class Index(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        data = {
            'error': self.request.get('error'),
            'user': user,
            'mosaics': list(MosaicImage.all().filter("user =", user))
        }

        if users.get_current_user():
            data["logurl"] = users.create_logout_url(self.request.uri)
            data["logtext"] = "log out"
        else:
            data["logurl"] = users.create_login_url(self.request.uri)
            data["logtext"] = "log in"

        self.response.out.write(template.render('index.html', data))
