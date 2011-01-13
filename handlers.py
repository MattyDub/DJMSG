# Copyright 2011 Matthew Wyatt
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.appengine.api import users
from google.appengine.api import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.db import GqlQuery
from google.appengine.ext.webapp import template
import models
import os, logging

#The below class is based on the MainHandler created by Google Inc.,
#(c) 2007
class MainHandler(webapp.RequestHandler):
    @login_required
    def get(self):
	logging.debug("MainHandler.get")
	user = users.get_current_user()
	if user:
	    #TODO: set up session stuff?
	    query = models.Game.all()
	    query.filter('user = ', user)
	    template_values = {}
	    results = query.fetch(10)
	    template_values['games'] = results
	    template_values['name'] = user.nickname()
	    template_values['url'] = users.create_logout_url(self.request.uri)
	    path = os.path.join(os.path.dirname(__file__), 'index.html')
	    self.response.out.write(template.render(path, template_values))
	else:
	    pass # do redirect to login here? Is this possible with @login_required?
	
class GameStart(webapp.RequestHandler):
    def post(self):
	#DANGER NOT SANITIZED!
	address = self.request.get("address")
	logging.info('Trying to start game with email address: ' + address)
	taskqueue.add(url='/tasks/start', params={'address':address})
	# TODO: make idempotent
	self.redirect('/')

class GameStartTask(webapp.RequestHandler):
    def post(self):
	address = self.request.get('address')
	logging.info('Trying to start game with ' + address)
	#Create game in data store
	#Get id for game
	# Create HTML email containing form for the opponent to join
