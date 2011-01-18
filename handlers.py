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
from google.appengine.api import mail
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.db import GqlQuery, run_in_transaction
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
	#TODO: DANGER NOT SANITIZED!
	address = self.request.get("address")
	logging.info('Trying to start game with email address: ' + address)
	taskqueue.add(url='/tasks/start', params={'address':address,
						  'player':users.get_current_user().email()})
	# TODO: make idempotent
	self.redirect('/')

class GameJoinHandler(webapp.RequestHandler):
    @login_required
    def get(self, id):
	id = int(id)
	user = users.get_current_user()
	game = models.Game.get_by_id(id)
	if game:
	    logging.info("players for game " + str(id))
	    for p in game.players:
		logging.info(p)
	    if user in game.players:
		template_values = {}
		state = game.state
		opp= state.active_player.nickname()
		url = "http://msg.appspot.com/joingame/%d" % id
		template_values['opponent'] = opp
		template_vaules['url'] = url
		path = os.path.join(os.path.dirname(__file__), 'joingame.html')
		self.response.out.write(template.render(path, template_values))
	    else:
		self.response.out.write("You aren't authorized to see this game. If you feel you reached this message in error, please contact a site administrator.")
	else: #TODO: figure this out
	    self.response.out.write("You are trying to join a game that doesn't exist.  If you feel this is an error, please contact the site administrator.")

    def post(self, id):
	#TODO: actually start game: set up map, add joining player to
	#list of players, change game state to 'active'
        game = models.Game.get_by_id(id)
        user = users.get_current_user()
        if game and user:
            game.mapname = 'Open Field'
            game.players.append(user)
            state = game.state
            state.state = 'active'
            state.put()
            game.put()
        else: #no game or no user: TODO
            self.response.out.write("Either you aren't logged in, or you're trying to join a game that doesn't exist.  If you feel you have reached this message in error, please contact an administrator.")
	    
#TODO: starting and joining should be POST methods; how do we make a game join a POST?
class GameStartTask(webapp.RequestHandler):
    def post(self):
	address = self.request.get('address')
	starting_player = self.request.get('player')
	logging.info(starting_player + ' is trying to start game with ' + address)
	#Create game in data store
	user = users.User(starting_player)
	newstate = models.GameState(state='wait_for_player',
				    active_player = user)
	newstate.put()
	ps = []
	ps.append(user)
	game = models.Game(state = newstate, players = ps)
	game.put()
	newgameid = game.key().id()
	#Get id for game
	logging.info(('New game id = "%d"' % newgameid))
	# Create HTML email containing form for the opponent to join
	msg = mail.EmailMessage(to=address,
				sender=self.request.get('player'),
				subject='Shall we play a game?',
				html=('<html><body>You have been invited to play a game with %s. To do so, visit <a href="http://msg.appspot.com/joingame/%d">http://msg.appspot.com/joingame/%d</a>!' % (starting_player, newgameid, newgameid)))
	try:
	    msg.check_initialized()
	    msg.send()
	except mail.Error:
	    logging.error("Email message not initialized properly! " + type(e))
