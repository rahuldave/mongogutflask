// Generated by CoffeeScript 1.6.1
(function() {
  var $, h, inline_list, root;

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  $ = jQuery;

  console.log("In Funcs");

  h = teacup;

  inline_list = h.renderable(function(items) {
    return h.ul('.inline', function() {
      var i, _i, _len, _results;
      _results = [];
      for (_i = 0, _len = items.length; _i < _len; _i++) {
        i = items[_i];
        _results.push(h.li(i));
      }
      return _results;
    });
  });

  root.widgets = {
    inline_list: inline_list
  };

}).call(this);
