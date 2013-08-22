// Generated by CoffeeScript 1.6.1
(function() {
  var $, $one_col_table, $table_from_dict, dropdown_submit, dropdown_submit_with_cb, h, info_layout, inline_list, link, multiselect, one_col_table, one_col_table_partial, one_submit, one_submit_with_cb, postalall_form, postalnote_form, regular_list, root, single_button, single_button_label, table_from_dict, table_from_dict_partial;

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

  regular_list = h.renderable(function(items) {
    return h.ul('.regular', function() {
      var i, _i, _len, _results;
      _results = [];
      for (_i = 0, _len = items.length; _i < _len; _i++) {
        i = items[_i];
        _results.push(h.li(i));
      }
      return _results;
    });
  });

  table_from_dict_partial = h.renderable(function(k, v) {
    h.td(k);
    return h.td(function() {
      return h.raw(v);
    });
  });

  table_from_dict = h.renderable(function(kcol, vcol, dict) {
    return h.table('.table.table-bordered.table-condensed.table-striped', function() {
      h.thead(function() {
        return h.tr(function() {
          h.th(kcol);
          return h.th(vcol);
        });
      });
      return h.tbody(function() {
        var k, v, _results;
        _results = [];
        for (k in dict) {
          v = dict[k];
          _results.push(h.tr(function() {
            return table_from_dict_partial(k, v);
          }));
        }
        return _results;
      });
    });
  });

  $table_from_dict = function(kcol, vcol, vlist) {
    var $f, f, k, _i, _len;
    f = h.renderable(function(kcol, vcol) {
      return h.table('.table.table-bordered.table-condensed.table-striped', function() {
        h.thead(function() {
          return h.tr(function() {
            h.th(kcol);
            return h.th(vcol);
          });
        });
        return h.tbody;
      });
    });
    $f = $(f(kcol, vcol));
    for (_i = 0, _len = vlist.length; _i < _len; _i++) {
      k = vlist[_i];
      $f.append(k);
    }
    return $f;
  };

  one_col_table_partial = h.renderable(function(k) {
    console.log("HTMLOUT", k, h.html);
    return h.td(function() {
      return h.raw(k);
    });
  });

  one_col_table = h.renderable(function(kcol, tlist) {
    return h.table('.table.table-bordered.table-condensed', function() {
      h.thead(function() {
        return h.tr(function() {
          return h.th(kcol);
        });
      });
      return h.tbody(function() {
        var k, _i, _len, _results;
        _results = [];
        for (_i = 0, _len = tlist.length; _i < _len; _i++) {
          k = tlist[_i];
          _results.push(h.tr(function() {
            return one_col_table_partial(k);
          }));
        }
        return _results;
      });
    });
  });

  $one_col_table = function(kcol, vlist) {
    var $f, f, k, _i, _len;
    f = h.renderable(function(kcol) {
      return h.table('.table.table-bordered.table-condensed', function() {
        h.thead(function() {
          return h.tr(function() {
            return h.th(kcol);
          });
        });
        return h.tbody;
      });
    });
    $f = $(f(kcol));
    for (_i = 0, _len = vlist.length; _i < _len; _i++) {
      k = vlist[_i];
      $f.append(k);
    }
    return $f;
  };

  one_submit = h.renderable(function(ltext, btext) {
    h.label(ltext);
    return h.form(".form-inline", function() {
      h.input(".span3.txt", {
        type: 'text'
      });
      h.raw("&nbsp;&nbsp;&nbsp;");
      return h.button(".btn.btn-primary.sub", {
        type: 'button'
      }, btext);
    });
  });

  one_submit_with_cb = h.renderable(function(ltext, btext, ctext) {
    h.label(ltext);
    return h.form(".form-inline", function() {
      h.input(".span3.txt", {
        type: 'text'
      });
      h.raw("&nbsp;&nbsp;");
      h.label('.checkbox', function() {
        h.input(".cb", {
          type: 'checkbox'
        });
        return h.text(ctext);
      });
      h.raw("&nbsp;&nbsp;&nbsp;");
      return h.button(".btn.btn-primary.sub", {
        type: 'button'
      }, btext);
    });
  });

  dropdown_submit = h.renderable(function(selects, ltext, btext) {
    h.label(ltext);
    return h.form('##{wname}.form-inline', function() {
      h.select(".sel", function() {
        var s, _i, _len, _results;
        _results = [];
        for (_i = 0, _len = selects.length; _i < _len; _i++) {
          s = selects[_i];
          _results.push(h.option(s));
        }
        return _results;
      });
      h.raw("&nbsp;&nbsp;&nbsp;");
      return h.button(".btn.btn-primary.sub", {
        type: 'button'
      }, btext);
    });
  });

  dropdown_submit_with_cb = h.renderable(function(selects, ltext, btext, ctext) {
    h.label(ltext);
    return h.form('.form-inline', function() {
      h.select(".sel", function() {
        var s, _i, _len, _results;
        _results = [];
        for (_i = 0, _len = selects.length; _i < _len; _i++) {
          s = selects[_i];
          _results.push(h.option(s));
        }
        return _results;
      });
      h.raw("&nbsp;&nbsp;");
      h.label('.checkbox', function() {
        h.input(".cb", {
          type: 'checkbox'
        });
        return h.text(ctext);
      });
      h.raw("&nbsp;&nbsp;&nbsp;");
      return h.button(".btn.btn-primary.sub", {
        type: 'button'
      }, btext);
    });
  });

  info_layout = h.renderable(function(dict, keysdict) {
    return h.dl('.dl-horizontal', function() {
      var k, _results;
      _results = [];
      for (k in keysdict) {
        h.dt(keysdict[k]);
        _results.push(h.dd(dict[k]));
      }
      return _results;
    });
  });

  single_button = h.renderable(function(btext) {
    return h.button('.btn.btn-mini.btn-primary.yesbtn', {
      type: 'button'
    }, btext);
  });

  single_button_label = h.renderable(function(ltext, btext) {
    h.text(ltext);
    h.raw("&nbsp;&nbsp;");
    return h.button('.btn.btn-mini.btn-primary.yesbtn', {
      type: 'button'
    }, btext);
  });

  postalnote_form = h.renderable(function(htmlstring, additional, btext) {
    h.raw(htmlstring);
    h.br();
    h.raw(additional);
    h.textarea(".controls.input-xlarge.txt", {
      type: "text",
      rows: '2',
      placeholder: "Type a note"
    });
    h.label(".control-label", function() {
      h.input(".control.cb", {
        type: 'checkbox'
      });
      h.text("note private?");
      return h.raw("&nbsp;&nbsp;");
    });
    return h.button('.btn.btn-primary.btn-mini.notebtn', {
      type: 'button'
    }, btext);
  });

  multiselect = h.renderable(function(daclass, choices) {
    return h.select(".multi" + daclass, {
      multiple: "multiple"
    }, function() {
      var c, _i, _len, _results;
      _results = [];
      for (_i = 0, _len = choices.length; _i < _len; _i++) {
        c = choices[_i];
        _results.push(h.option(c));
      }
      return _results;
    });
  });

  postalall_form = h.renderable(function(nameable, itemtype, groupchoices, librarychoices) {
    h.legend("Post ALL");
    if (nameable) {
      h.div(".control-group", function() {
        h.label(".control-label", "Name this " + itemtype);
        return h.input(".controls", {
          type: text,
          placeholder: "Name for " + itemtype
        });
      });
    }
    h.div(".control-group", function() {
      return h.label(".checkbox.control-label", function() {
        h.input(".controls.makepublic", {
          type: "checkbox"
        });
        return h.text("Make Public");
      });
    });
    h.div(".control-group", function() {
      h.label(".control-label", "Libraries");
      return multiselect("library", librarychoices);
    });
    h.div(".control-group", function() {
      h.label(".control-label", "Groups");
      return multiselect("group", groupchoices);
    });
    h.button(".btn.btn-primary.post", {
      type: 'button'
    }, "Post");
    h.br();
    h.br();
    h.legend("Tag ALL");
    h.input(".controls.tagsinput.input-xxlarge", {
      type: "text",
      placeholder: "Tag names, comma separated"
    });
    h.button(".btn.btn-primary.tag", {
      type: 'button'
    }, "Tag");
    h.br();
    return h.button(".btn.btn-inverse.done.pull-right", {
      type: 'button'
    }, "I'm done");
  });

  link = h.renderable(function(url, txt) {
    return h.raw("<a href=\"" + url + "\">" + txt + "</a>");
  });

  root.widgets = {
    postalall_form: postalall_form,
    postalnote_form: postalnote_form,
    single_button: single_button,
    single_button_label: single_button_label,
    inline_list: inline_list,
    regular_list: regular_list,
    info_layout: info_layout,
    one_col_table_partial: one_col_table_partial,
    table_from_dict_partial: table_from_dict_partial,
    one_col_table: one_col_table,
    $one_col_table: $one_col_table,
    table_from_dict: table_from_dict,
    $table_from_dict: $table_from_dict,
    one_submit: one_submit,
    dropdown_submit: dropdown_submit,
    one_submit_with_cb: one_submit_with_cb,
    dropdown_submit_with_cb: dropdown_submit_with_cb,
    link: link
  };

}).call(this);
