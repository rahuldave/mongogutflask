(function(){

	// the minimum version of jQuery we want
	var v = "1.3.2";
	alert("hi0");
	// check prior inclusion and version
	if (window.jQuery === undefined || window.jQuery.fn.jquery < v) {
		var done = false;
		var script = document.createElement("script");
		script.src = "http://ajax.googleapis.com/ajax/libs/jquery/" + v + "/jquery.min.js";
		alert("hi1");
		script.onload = script.onreadystatechange = function(){
			if (!done && (!this.readyState || this.readyState == "loaded" || this.readyState == "complete")) {
				done = true;
				initMyBookmarklet();
			}
		};
		document.getElementsByTagName("head")[0].appendChild(script);
	} else {
		alert("hi3");
		initMyBookmarklet();
	}
	
	function initMyBookmarklet() {
		alert("hi2");
		(window.myBookmarklet = function() {
			// your JavaScript code goes here!
			var items=[];
			$(".searchresult > .span1 > .checkbox > input:checked").each(
					function(){items.push($(this).attr("value"));}); 
			var itemstring=items.join(":");
			alert("ITEMSTRING=", itemstring);
			open("http://localhost:4000/postform/html?items="+itemstring, width="750", height="300");
		})();
	}

})();

