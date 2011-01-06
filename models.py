from google.appengine.ext import db
from google.appengine.api import users

class Unit(db.Model):
    player = db.UserProperty(required=True)
    kind = db.StringProperty(required=True, choices = set(['Infantry','Cavalry','Archers']))
    xpos = db.IntProperty()
    ypos = db.IntProperty()
    attack = db.StringProperty() # This is iffy

class GameState(db.Model):
    units = db.ListProperty(Unit)
    active_player = db.UserProperty()

class Game(db.Model):
    map = db.StringProperty()
    players = db.ListProperty(users.User)
    state = db.ReferenceProperty(GameState)
    
