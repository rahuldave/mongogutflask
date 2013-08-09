root = exports ? this
$=jQuery
console.log "In Funcs"
h = teacup

inline_list = h.renderable (items) ->
    h.ul '.inline',  ->
        for i in items
            h.li i

table_from_dict = h.renderable (kcol, vcol, dict) ->
    h.table '.table.table-bordered.table-condensed',  ->
        h.thead ->
            h.tr ->
                h.th kcol
                h.th vcol
        h.tbody ->
            for k,v of dict
                h.tr ->
                    h.td k
                    h.td v
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

root.widgets = 
    inline_list: inline_list
    table_from_dict: table_from_dict
    one_submit: one_submit
    dropdown_submit: dropdown_submit
    one_submit_with_cb: one_submit_with_cb
    dropdown_submit_with_cb: dropdown_submit_with_cb