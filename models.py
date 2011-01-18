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

from google.appengine.ext import db
from google.appengine.api import users

class GameState(db.Model):
    active_player = db.UserProperty()
    state = db.StringProperty(choices = ('wait_for_player','active','complete'))

class Unit(db.Model):
    player = db.UserProperty(required=True)
    unit_type = db.StringProperty(required=True,
                                  choices = set(['Infantry','Cavalry','Archers']))
    xpos = db.IntegerProperty()
    ypos = db.IntegerProperty()
    attack = db.StringProperty() # This is iffy - don't know how this will work yet
    state = db.ReferenceProperty(GameState, collection_name='units')

class Game(db.Model):
    mapname = db.StringProperty() # name of map
    idhash = db.StringProperty() # md5 hash to id game
    players = db.ListProperty(users.User)
    state = db.ReferenceProperty(GameState)
    
