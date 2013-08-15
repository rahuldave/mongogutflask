// Generated by CoffeeScript 1.6.1
(function() {
  var $, Postable, PostableList, PostableListView, PostableView, h, parse_userinfo, root, w,
    __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
    _this = this;

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  $ = jQuery;

  console.log("In Funcs");

  h = teacup;

  w = widgets;

  parse_userinfo = function(data) {
    var e, postablesin, postablesinvitedto, postablesowned, priv, publ, userdict;
    publ = "adsgut/group:public";
    priv = data.user.nick + "/group:default";
    postablesin = data.user.postablesin;
    postablesowned = data.user.postablesowned;
    postablesinvitedto = data.user.postablesinvitedto;
    userdict = {
      groupsin: (function() {
        var _i, _len, _ref, _results;
        _results = [];
        for (_i = 0, _len = postablesin.length; _i < _len; _i++) {
          e = postablesin[_i];
          if (e.ptype === 'group' && ((_ref = e.fqpn) !== publ && _ref !== priv)) {
            _results.push(e.fqpn);
          }
        }
        return _results;
      })(),
      groupsowned: (function() {
        var _i, _len, _ref, _results;
        _results = [];
        for (_i = 0, _len = postablesowned.length; _i < _len; _i++) {
          e = postablesowned[_i];
          if (e.ptype === 'group' && ((_ref = e.fqpn) !== publ && _ref !== priv)) {
            _results.push(e.fqpn);
          }
        }
        return _results;
      })(),
      groupsinvitedto: (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = postablesinvitedto.length; _i < _len; _i++) {
          e = postablesinvitedto[_i];
          if (e.ptype === 'group') {
            _results.push(e.fqpn);
          }
        }
        return _results;
      })(),
      librariesin: (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = postablesin.length; _i < _len; _i++) {
          e = postablesin[_i];
          if (e.ptype === 'library') {
            _results.push(e.fqpn);
          }
        }
        return _results;
      })(),
      librariesowned: (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = postablesowned.length; _i < _len; _i++) {
          e = postablesowned[_i];
          if (e.ptype === 'library') {
            _results.push(e.fqpn);
          }
        }
        return _results;
      })(),
      librariesinvitedto: (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = postablesinvitedto.length; _i < _len; _i++) {
          e = postablesinvitedto[_i];
          if (e.ptype === 'library') {
            _results.push(e.fqpn);
          }
        }
        return _results;
      })(),
      userinfo: {
        nick: data.user.nick,
        whenjoined: data.user.basic.whencreated,
        name: data.user.basic.name
      }
    };
    return userdict;
  };

  Postable = (function(_super) {

    __extends(Postable, _super);

    function Postable() {
      return Postable.__super__.constructor.apply(this, arguments);
    }

    return Postable;

  })(Backbone.Model);

  PostableView = (function(_super) {

    __extends(PostableView, _super);

    function PostableView() {
      var _this = this;
      this.render = function() {
        return PostableView.prototype.render.apply(_this, arguments);
      };
      return PostableView.__super__.constructor.apply(this, arguments);
    }

    PostableView.prototype.tagName = "tr";

    PostableView.prototype.render = function() {
      var content;
      if (this.model.get('invite')) {
        this.$el.html(w.table_from_dict_partial(this.model.get('fqpn'), w.yes_button('Yes')));
      } else {
        content = w.one_col_table_partial(this.model.get('fqpn'));
        this.$el.html(content);
      }
      return this;
    };

    return PostableView;

  })(Backbone.View);

  PostableList = (function(_super) {

    __extends(PostableList, _super);

    function PostableList() {
      return PostableList.__super__.constructor.apply(this, arguments);
    }

    PostableList.prototype.model = Postable;

    PostableList.prototype.initialize = function(models, options) {
      this.listtype = options.listtype;
      return this.invite = options.invite;
    };

    return PostableList;

  })(Backbone.Collection);

  PostableListView = (function(_super) {

    __extends(PostableListView, _super);

    function PostableListView() {
      var _this = this;
      this.render = function() {
        return PostableListView.prototype.render.apply(_this, arguments);
      };
      return PostableListView.__super__.constructor.apply(this, arguments);
    }

    PostableListView.prototype.tmap = {
      "in": "In",
      ow: "Owned",
      iv: "Invited"
    };

    PostableListView.prototype.initialize = function(options) {
      return this.$el = options.$e_el;
    };

    PostableListView.prototype.render = function() {
      var $widget, m, v, views, _i, _len;
      console.log("h2", this.collection);
      views = (function() {
        var _i, _len, _ref, _results;
        _ref = this.collection.models;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          m = _ref[_i];
          _results.push(new PostableView({
            model: m
          }));
        }
        return _results;
      }).call(this);
      for (_i = 0, _len = views.length; _i < _len; _i++) {
        v = views[_i];
        console.log("h3", v.render().el);
      }
      if (this.collection.invite) {
        $widget = w.$table_from_dict("Invitations", "Accept?", (function() {
          var _j, _len1, _results;
          _results = [];
          for (_j = 0, _len1 = views.length; _j < _len1; _j++) {
            v = views[_j];
            _results.push(v.render().el);
          }
          return _results;
        })());
      } else {
        $widget = w.$one_col_table(this.tmap[this.collection.listtype], (function() {
          var _j, _len1, _results;
          _results = [];
          for (_j = 0, _len1 = views.length; _j < _len1; _j++) {
            v = views[_j];
            _results.push(v.render().el);
          }
          return _results;
        })());
      }
      return this.$el.append($widget);
    };

    return PostableListView;

  })(Backbone.View);

  root.userprofile = {
    parse_userinfo: parse_userinfo,
    Postable: Postable,
    PostableList: PostableList,
    PostableListView: PostableListView
  };

}).call(this);
