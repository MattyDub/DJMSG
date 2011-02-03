var msgvis = function (mapdata, gamedata) {
    return function() {
	var r = Raphael("holder", 640,480);
	var kHexPath = "M20 20 l40 0 l20 32 l-20 32 l-40 0 l-20 -32 z";
	var makehandler = function (obj) {
            return function(e) {
		console.log(obj.x, obj.y);
            }
	};
	var drawGrass = function() {
	    var d = r.path("M15 40 l20 20 l20 -20z");
	    d.attr({fill:"#000"});
	    return d;
	};
	var drawForest = function() {
	    var d = r.path("M15 40 l20 20 l20 -20z");
	    d.attr({fill:"#777"});
	    return d;
	};
	var drawHills = function() {
	    var d = r.path("M15 40 l20 20 l20 -20z");
	    d.attr({fill:"#fff"});
	    return d;
	};
	var drawterrain = {"g":drawGrass,"f":drawForest,"h":drawHills};
	var fill = {"g":"rgb(0,200,0)","f":"rgb(0,100,0)","h":"rgb(80,80,0)"};
	var maketerrain = function(x,y, terrain) {
	    var s = r.set();
            var h = r.path(kHexPath);
            h.attr({fill:fill[terrain]});
	    var d = drawterrain[terrain]();
	    var cov = r.path(kHexPath);
	    cov.attr({fill:"#000",opacity:0});
	    cov.x = x; cov.y = y;
	    cov.node.onclick = makehandler(cov);
	    s.push(h,d,cov);
	    return s;
	}
	var makehex = function(x,y,terrain) {
            var tx, ty, vertshift, h;
	    h = maketerrain(x,y, terrain);
            vertshift = ((x % 2) === 1 ? 32 : 0);
            h.translate(62 * x, (64 * y) + vertshift);
	};
	var i,ii,j,jj,rs,cs;
	jj = mapdata.length;
	ii = mapdata[0].length;
	for (j = 0; j < jj; j++) {
	    for (i = 0; i < ii; i++) {
		makehex(i,j,mapdata[j][i]);
	    }
	}
    };
};
window.onload = msgvis(msg_maps.small,gamestate);