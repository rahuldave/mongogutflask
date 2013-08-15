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
    h.td ->
        h.raw v

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
        h.button ".btn.btn-primary", type: 'button', btext

one_submit_with_cb = h.renderable (ltext, btext, ctext) ->
    h.label ltext
    h.form ".form-inline", ->
        h.input ".span3", type: 'text'
        h.label '.checkbox', ->
            h.input type: 'checkbox'
            h.text ctext
        h.button ".btn.btn-primary", type: 'button', btext

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
        h.button ".btn.btn-primary", type: 'button', btext

info_layout = h.renderable (dict, keysdict) ->
  h.dl '.dl-horizontal', ->
    for k of keysdict
        h.dt keysdict[k]
        h.dd dict[k]

#<button class="btn btn-small" type="button">Small button</button> 
yes_button = h.renderable (btext) ->
    h.button '.btn.btn-mini.btn-primary', type:'button', btext

# <div class=\"control-group\">
#   <label class=\"control-label\">Add Note</label>
#   <input type=\"text\" class=\"controls input-xxlarge\" placeholder=\"Type a note…\">
#   <label class=\"checkbox control-label\">
#     <input type=\"checkbox\" class=\"controls\"> Make Private
#   </label>
# </div>

postalnote_form = h.renderable () ->
    h.div ".control-group.postalnote", ->
        h.textarea ".controls.input-xlarge", type:"text", rows:'2', placeholder:"Type a note"
        h.label ".checkbox.control-label", ->
            h.input ".controls", type:'checkbox'
            h.text "Make note Private"

#     <legend>Tagging and Posting</legend>
#     {% if nameable %}
#       <div class="control-group">
#         <label class="control-label">Name this {{itemtype}}</label>
#         <input class="controls" type="text" placeholder="Name for {{itemtype}}…">
#       </div>
#     {% endif %}
#     <div class="control-group">
#       <label class="checkbox control-label">
#         <input class="controls" type="checkbox"> Make Public
#       </label>
#     </div>
#     <div class="control-group">
#       <label id="libslabel" class="control-label">Libraries</label>
#       <input class="controls" type="text" placeholder="Library Name…">
#     </div>
#     <div class="control-group">
#       <label id="groupslabel" class="control-label">Groups</label>
#       <input class="controls" type="text" placeholder="Group Name…">
#     </div>
#     <div class="control-group">
#       <label class="control-label">Tags</label>
#       <input class="controls" type="text" placeholder="Tag Name…">
#     </div>
#     <button type="submit" class="btn">Submit</button>


postalall_form = h.renderable (nameable, itemtype) ->
    h.legend "Tagging and Posting"
    if nameable
        h.div ".control-group", ->
            h.label ".control-label", "Name this #{itemtype}"
            h.input ".controls", type:text, placeholder:"Name for #{itemtype}"
    h.div ".control-group", ->
        h.label ".checkbox.control-label", ->
            h.input ".controls.makepublic", type:"checkbox"
            h.text "Make Public"
    h.div ".control-group", ->
        h.label ".control-label", "Libraries"
        h.input ".controls.librariesinput.input-xxlarge", type:"text", placeholder:"Lib names, comma separated" 
    h.div ".control-group", ->
        h.label ".control-label", "Groups"
        h.input ".controls.groupsinput.input-xxlarge", type:"text", placeholder:"Grp names, comma separated"
    h.div ".control-group", ->
        h.label ".control-label", "Tags"
        h.input ".controls.tagsinput.input-xxlarge", type:"text", placeholder:"Tag names, comma separated"
    h.button ".btn.btn-primary", type:'button', "Save"


root.widgets = 
    postalall_form: postalall_form
    postalnote_form: postalnote_form
    yes_button: yes_button
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