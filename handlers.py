from google.appengine.ext import webapp
from google.appengine.api import users

class MainHandler(webapp.RequestHandler):
    def get(self):
	user = users.get_current_user()
	if user:
	    message = ('Hello, %s' % user.nickname())
	else:
	    message = ('Hello world!')
	self.response.out.write(message)
