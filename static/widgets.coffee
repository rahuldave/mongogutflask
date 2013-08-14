root = exports ? this
$=jQuery
console.log "In Funcs"
h = teacup

inline_list = h.renderable (items) ->
    h.ul '.inline',  ->
        for i in items
            h.li i

regular_list = h.renderable (items) ->
    h.ul '.regular',  ->
        for i in items
            h.li i

table_from_dict_partial = h.renderable (k,v) ->
    h.td k
    h.td v

table_from_dict = h.renderable (kcol, vcol, dict) ->
    h.table '.table.table-bordered.table-condensed.table-striped',  ->
        h.thead ->
            h.tr ->
                h.th kcol
                h.th vcol
        h.tbody ->
            for k,v of dict
                h.tr ->
                    table_from_dict_partial(k,v)

$table_from_dict = (kcol, vcol, vlist) ->
    f=h.renderable (kcol, vcol) ->
        h.table '.table.table-bordered.table-condensed.table-striped',  ->
            h.thead ->
                h.tr ->
                    h.th kcol
                    h.th vcol
            h.tbody
    $f=$(f(kcol,vcol))
    for k in vlist
        $f.append(k)
    return $f


one_col_table_partial = h.renderable (k) ->
    h.td k

one_col_table = h.renderable (kcol, tlist) ->
    h.table '.table.table-bordered.table-condensed',  ->
        h.thead ->
            h.tr ->
                h.th kcol
        h.tbody ->
            for k in tlist
                h.tr ->
                    one_col_table_partial k

$one_col_table = (kcol, vlist) ->
    f=h.renderable (kcol) ->
        h.table '.table.table-bordered.table-condensed',  ->
            h.thead ->
                h.tr ->
                    h.th kcol
            h.tbody
    $f=$(f(kcol))
    for k in vlist
        $f.append(k)
    return $f

# <div class="input-append">
#   <input class="span2" id="appendedInputButton" type="text">
#   <button class="btn" type="button">Go!</button>
# </div>
#one_submit needs to have an event handler added
one_submit = h.renderable (ltext, btext) ->
    h.label ltext
    h.form ".form-inline", ->
        h.input ".span3", type: 'text'
        h.button ".btn", type: 'button', btext

one_submit_with_cb = h.renderable (ltext, btext, ctext) ->
    h.label ltext
    h.form ".form-inline", ->
        h.input ".span3", type: 'text'
        h.label '.checkbox', ->
            h.input type: 'checkbox'
            h.text ctext
        h.button ".btn", type: 'button', btext

dropdown_submit = h.renderable (selects, ltext, btext) ->
    h.label ltext
    h.form '##{wname}.form-inline', ->
        h.select ->
            for s in selects
                h.option s
        h.button ".btn", type: 'button', btext

dropdown_submit_with_cb = h.renderable (selects, ltext, btext, ctext) ->
    h.label ltext
    h.form '.form-inline', ->
        h.select ->
            for s in selects
                h.option s
        h.label '.checkbox', ->
            h.input type: 'checkbox'
            h.text ctext
        h.button ".btn", type: 'button', btext

info_layout = h.renderable (dict, keysdict) ->
  h.dl '.dl-horizontal', ->
    for k of keysdict
        h.dt keysdict[k]
        h.dd dict[k]
    

root.widgets = 
    inline_list: inline_list
    regular_list: regular_list
    info_layout: info_layout
    one_col_table_partial: one_col_table_partial
    table_from_dict_partial: table_from_dict_partial
    one_col_table: one_col_table
    $one_col_table: $one_col_table
    table_from_dict: table_from_dict
    $table_from_dict: $table_from_dict
    one_submit: one_submit
    dropdown_submit: dropdown_submit
    one_submit_with_cb: one_submit_with_cb
    dropdown_submit_with_cb: dropdown_submit_with_cb