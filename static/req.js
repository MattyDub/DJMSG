/*
  Copyright 2011 Matthew Wyatt

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/
/*
  msgreq is a module which has one function, getState.

  getState takes a callback and a game id.  The callback is called
when the game state for that game id is returned, and passes the state
to the callback.  The callback needs to check for error conditions!
*/
var msgreq = (function () {
    return {
	getState: function(callback, gameid) {
	    //This code is based on the article at
	    //http://code.google.com/appengine/articles/rpc.html
	    //that code's copyright is held by Google, as of 2011,
	    //and is licensed under the Apache 2.0 license.
	    //(All of the code in this project is also Apache 2.0.)
	    var req = new XMLHttpRequest();
	    req.open('GET', '/gamestate/' + gameid, true);

	    req.onreadystatechange = function() {
		if(req.readyState == 4 && req.status == 200) {
		    var response = null;
		    try {
			response = JSON.parse(req.responseText);
		    } catch (e) {
			response = req.responseText;
		    }
		    callback(response);
		}
	    }
	    req.send(null);
	}
    };
})();
