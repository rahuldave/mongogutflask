// Generated by CoffeeScript 1.6.1
(function() {
  var $, PostableListView, PostableView, h, root, w,
    _this = this,
    __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  $ = jQuery;

  console.log("In libraryprofile");

  h = teacup;

  w = widgets;

  PostableView = (function(_super) {

    __extends(PostableView, _super);

    function PostableView() {
      var _this = this;
      this.clickedToggle = function() {
        return PostableView.prototype.clickedToggle.apply(_this, arguments);
      };
      this.render = function() {
        return PostableView.prototype.render.apply(_this, arguments);
      };
      return PostableView.__super__.constructor.apply(this, arguments);
    }

    PostableView.prototype.tagName = "tr";

    PostableView.prototype.events = {
      "click .yesbtn": "clickedToggle"
    };

    PostableView.prototype.initialize = function(options) {
      this.rwmode = options.rwmode, this.memberable = options.memberable, this.fqpn = options.fqpn;
      return console.log("PVIN", this.rwmode, this.memberable, this.fqpn);
    };

    PostableView.prototype.render = function() {
      var content;
      content = w.table_from_dict_partial(this.memberable, w.single_button_label(this.rwmode, "Toggle"));
      console.log("CONTENT", content, this.rwmode, this.memberable, this.fqpn);
      this.$el.html(content);
      return this;
    };

    PostableView.prototype.clickedToggle = function() {
      var cback, eback, loc;
      loc = window.location;
      cback = function(data) {
        console.log("return data", data, loc);
        return window.location = location;
      };
      eback = function(xhr, etext) {
        console.log("ERROR", etext, loc);
        return alert('Did not succeed');
      };
      console.log("GGG", this.model, this.$el);
      return syncs.toggle_rw(this.memberable, this.fqpn, cback, eback);
    };

    return PostableView;

  })(Backbone.View);

  PostableListView = (function(_super) {

    __extends(PostableListView, _super);

    function PostableListView() {
      var _this = this;
      this.render = function() {
        return PostableListView.prototype.render.apply(_this, arguments);
      };
      return PostableListView.__super__.constructor.apply(this, arguments);
    }

    PostableListView.prototype.initialize = function(options) {
      this.$el = options.$e_el;
      this.fqpn = options.fqpn;
      this.users = options.users;
      return this.owner = options.owner;
    };

    PostableListView.prototype.render = function() {
      var $widget, k, rendered, u, userlist, v, views;
      console.log("RENDERING", this.owner);
      if (this.owner === 'True') {
        views = (function() {
          var _results;
          _results = [];
          for (u in this.users) {
            _results.push(new PostableView({
              rwmode: this.users[u],
              fqpn: this.fqpn,
              memberable: u
            }));
          }
          return _results;
        }).call(this);
        rendered = (function() {
          var _i, _len, _results;
          _results = [];
          for (_i = 0, _len = views.length; _i < _len; _i++) {
            v = views[_i];
            _results.push(v.render().el);
          }
          return _results;
        })();
        console.log("RENDER1", rendered);
        console.log("RENDER2");
        $widget = w.$table_from_dict("User", "Can User/Group Post?", rendered);
        this.$el.append($widget);
      } else {
        userlist = (function() {
          var _ref, _results;
          _ref = this.users;
          _results = [];
          for (k in _ref) {
            v = _ref[k];
            _results.push(k);
          }
          return _results;
        }).call(this);
        this.$el.html(w.inline_list(userlist));
      }
      return this;
    };

    return PostableListView;

  })(Backbone.View);

  root.libraryprofile = {
    PostableView: PostableView,
    PostableListView: PostableListView
  };

}).call(this);
