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
#

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
