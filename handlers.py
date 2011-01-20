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
from hashlib import md5

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
            query.filter('players = ', user)
            template_values = {}
            results = query.fetch(10)
            logging.info("There are %d game(s) for logged-in user %s" % (len(results), user))
            logging.info(type(results[0]))
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
        taskqueue.add(url='/tasks/start',
                      params={'address':address,
                              'player':users.get_current_user().email()})
        # TODO: make idempotent
        self.redirect('/')

class GameJoinHandler(webapp.RequestHandler):
    @login_required
    def get(self, id):
        user = users.get_current_user()
        query = models.Game.all()
        query.filter('idhash = ', id)
        results = query.fetch(1) # TODO: is there a better way to do this?
        if results:
            logging.info("# of games for hash = " + str(len(results)))
            game = results[0]
            logging.info("players for game " + str(id))
            for p in game.players:
                logging.info(p)
            template_values = {}
            state = game.state
            opp= state.active_player.nickname()
            url = "/joingame/%s" % id
            template_values['opponent'] = opp
            template_values['url'] = url
            path = os.path.join(os.path.dirname(__file__), 'joingame.html')
            self.response.out.write(template.render(path, template_values))
        else: #TODO: figure this out
            self.response.out.write("You are trying to join a game that doesn't exist.  If you feel this is an error, please contact the site administrator.")

    def post(self, id):
        logging.info("Invited player joining game " + id)
        query = models.Game.all()
        query.filter('idhash = ', id)
        results = query.fetch(1) # TODO: is there a better way to do this?
        if results and len(results) > 0:
            logging.info("%d game(s) found to join, joining first" % len(results))
            game = results[0]
            user = users.get_current_user()
            if game and user:
                game.mapname = 'Open Field'
                l1 = game.players
                game.players.append(user)
                l2 = game.players
                logging.info("Before, players were: " +
                             ",".join([str(l) for l in l1]))
                logging.info("After, players are  : " +
                             ",".join([str(l) for l in l2]))
                state = game.state
                state.state = 'active'
                state.put()
                game.put()
                l = game.players
                self.redirect('/')
            else: #no game or no user: TODO
                self.response.out.write("Either you aren't logged in, or you're trying to join a game that doesn't exist.  If you feel you have reached this message in error, please contact an administrator.")
        else:
            self.response.out.write("You're trying to join a game that doesn't exist.  If you feel you reached this message in error, please contact an administrator.")
        
class PlayHandler(webapp.RequestHandler):
    @login_required
    def get(self, id):
        user = users.get_current_user()
        query = models.Game.all()
        query.filter('idhash = ', id)
        game = query.get()
        if user in game.players:
            state = game.state
            if user != state.active_player:
                logging.warn("Player %s tried to access game %s; not her turn"
                             % (user, id))
                self.redirect('/') #TODO: better idea?
            template_values = {}
            template_values['turn'] = state.turn
            path = os.path.join(os.path.dirname(__file__), 'play.html')
            self.response.out.write(template.render(path, template_values))
        else:
            logging.error("Player %s tried to access game %s, and wasn't found in datastore." % (user, id))
            self.response.out.write("You can't access this game")
            
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
        #Get id for game:
        newgameid = game.key().id()
        h = md5()
        h.update(str(newgameid))
        h.update(address)
        digest = h.hexdigest()
        game.idhash = digest
        game.put()
        logging.info(('New game id = "%d", md5 = %s' % (newgameid, digest)))
        # Create HTML email containing form for the opponent to join
        msg = mail.EmailMessage(to=address,
                                sender=self.request.get('player'),
                                subject='Shall we play a game?',
                                html=('<html><body>You have been invited to play a game with %s. To do so, visit <a href="http://msg.appspot.com/joingame/%s">http://msg.appspot.com/joingame/%s</a>!' % (starting_player, digest, digest)))
        try:
            msg.check_initialized()
            msg.send()
        except mail.Error:
            logging.error("Email message not initialized properly! " + type(e))
