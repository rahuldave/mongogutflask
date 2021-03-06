root = exports ? this
$=jQuery
console.log "In Funcs"
{renderable, ul, li, dl, dt, dd, raw, br, strong} = teacup
w = widgets

format_tags = (tagtype, $sel, tags, tagqkey)->
  htmlstring="<li class=\"nav-header\">#{tagtype}</li>"
  for [k,v] in tags
    if tagqkey is 'stags'
      t=v[0]
    else if tagqkey is 'tagname'
      t=k
    else
      t="CRAP"
    nonqloc=document.location.href.split('?')[0]
    if tagqkey is 'tagname'
      url=nonqloc+"?query=tagtype:#{tagtype}&query=#{tagqkey}:#{t}"
      urla=document.location+"&query=tagtype:#{tagtype}&query=#{tagqkey}:#{t}"
      if nonqloc is document.location.href
        urla=document.location+"?query=tagtype:#{tagtype}&query=#{tagqkey}:#{t}"
    else
      url=nonqloc+"?query=#{tagqkey}:#{t}"
      urla=document.location+"&query=#{tagqkey}:#{t}"
      if nonqloc is document.location.href
        urla=document.location+"?query=#{tagqkey}:#{t}"
    
    htmlstring = htmlstring+"<li><span><a href=\"#{url}\">#{k}</a>&nbsp;<a href=\"#{urla}\">(+)</a></span></li>"
    ##{v.join(',')}
  $sel.html(htmlstring)


format_notes_for_item = (fqin, notes, nick) ->
  t3list=("<span>#{t}</span><br/>" for t in notes[fqin])
  if t3list.length >0
    return "<p>Notes:<br/>"+t3list.join("<br/>")+"</p>"
  else
    return ""

format_tags_for_item = (fqin, stags, nick) ->
  t2list=("<a href=\"/postable/#{nick}/group:default/filter/html?query=tagname:#{t[0]}&query=tagtype:#{t[1]}\">#{t[0]}</a>" for t in stags[fqin])
  if t2list.length >0
    return "<span>Tagged as "+t2list.join(", ")+"</span><br/>"
  else
    return ""

format_postings_for_item = (fqin, postings, nick) ->
  p2list=("<a href=\"/postable/#{p}/filter/html\">#{p}</a>" for p in postings[fqin] when p isnt "#{nick}/group:default")
  if p2list.length >0
    return "<span>Posted in "+p2list.join(", ")+"</span><br/>"
  else
    return ""

format_stuff = (fqin, nick, stags, postings, notes) ->
  htmlstring= ""
  htmlstring= htmlstring+format_tags_for_item(fqin, stags, nick)
  htmlstring= htmlstring+format_postings_for_item(fqin, postings, nick)
  htmlstring= htmlstring+format_notes_for_item(fqin, notes, nick)
  return htmlstring

format_items = ($sel, nick, items, count, stags, notes, postings, formatter, asform=false) ->
  console.log "HTML", $sel.html()
  adslocation = "http://labs.adsabs.harvard.edu/adsabs/abs/"
  htmlstring = ""
  console.log items.length, "ITTABITTA", (i.basic.fqin for i in items), "}}"
  for i in items
    fqin=i.basic.fqin
    #console.log "whatsup", fqin, items.length, $sel, htmlstring
    url=adslocation + "#{i.basic.name}"
    htmlstring = htmlstring + "<#{formatter}><a href=\"#{url}\">#{i.basic.name}</a><br/>"
    htmlstring=htmlstring+format_tags_for_item(fqin, stags, nick)
    htmlstring=htmlstring+format_postings_for_item(fqin, postings, nick)
    htmlstring=htmlstring+format_notes_for_item(fqin, notes, nick)  
    htmlstring=htmlstring+"</#{formatter}>"
    if asform
      htmlstring=htmlstring+w.postalnote_form("make note")
  $sel.append(htmlstring)
  $('#breadcrumb').append("#{count} items")

get_tags = (tags, tqtype) ->
  console.log "TAGS", tags
  tdict={}
  if tqtype is 'stags'
    return ([t[3], [t[0]]] for t in tags)
  for t in tags
    [fqtn, user, type, name]=t
    if tdict[name] is undefined
      tdict[name]=[]
    tdict[name].push(fqtn)
  if tqtype is 'tagname'
    return ([k,v] for own k,v of tdict)
  return []

get_taggings = (data) ->
  stags={}
  notes={}
  console.log "DATA", data
  for own k,v of data.taggings
    #console.log "1>>>", k,v[0], v[1]
    if v[0] > 0
      stags[k]=([e.thething.tagname, e.thething.tagtype] for e in v[1] when e.thething.tagtype is "ads/tagtype:tag")
      notes[k]=(e.thething.tagdescription for e in v[1] when e.thething.tagtype is "ads/tagtype:note")
    else
      stags[k]=[]
      notes[k]=[]
    #console.log "HHHHH", stags[k], notes[k]
  return [stags, notes]

get_groups = (nick, cback) ->
  $.get "/user/#{nick}/groupsuserisin", (data) ->
    groups=data.groups
    cback(groups)



# #BUG: make backbone views for all of this
# postable_members_template = renderable (fqpn, users, owner, scmode=false) ->
#   if owner is 'True'
#     if scmode
#       userlist= (k for k,v of users)
#       w.one_col_table "Users", userlist
#     else
#       #w.table_from_dict("User", "Can User Write", users)
#       # v=PostableMembersView({$e_el:$e, fqpn:fqpn, users:users})
#       # return v.render()
#       views=(new RWToggleView({rwmode:users[u], fqpn:fqpn, memberable:u}) for u of users)
#       rendered = (v.render().el for v in views)
#       console.log "RENDER1", rendered
#       console.log "RENDER2"
#       $widget=w.$one_col_table("User", rendered)
#   else
#     userlist= (k for k,v of users)
#     w.inline_list userlist

postable_inviteds_template = renderable (fqpn, users, scmode=false) ->
  if scmode
    userlist= (k for k,v of users)
    w.one_col_table "Users", userlist
  else
    w.table_from_dict("User", "Can User Write", users)

# #Bug: these need to become collection Views
# postable_members = (fqpn, owner, data, template, scmode=false) ->
#   template(fqpn, data.users, owner, scmode)

postable_inviteds = (fqpn, data, template, scmode=false) ->
  template(fqpn, data.users, scmode)



postable_info_layout = renderable ({basic, owner}) ->
  url= "/postable/#{basic.fqin}/filter/html"
  a= "&nbsp;&nbsp;<a href=\"#{url}\">#{basic.fqin}</a>"
  dl '.dl-horizontal', ->
    dt "Description"
    dd basic.description
    dt "Owner"
    dd owner
    dt "Creator"
    dd basic.creator
    dt "Created on"
    dd basic.whencreated
  br()
  strong "Items:"
  raw a

library_info_template = renderable (data) ->
  postable_info_layout data.library

group_info_template = renderable (data) ->
  postable_info_layout data.group
  


#controller style stuff should be added here.
postable_info = (data, template) ->
  template(data)

#content=widgets.one_submit_with_cb("invite_user","Invite a user using their email:", "Invite", "Can Post?")
#$('div#invitedform').append(content)
#content=widgets.dropdown_submit_with_cb("add_group", ['a','b','c'],"Add a group you are a member of:","Add", "Can Post?")

class InviteUser extends Backbone.View

  tagName: 'div'

  events:
    "click .sub" : "inviteUserEH"

  initialize: (options) ->
    {@withcb, @postable} = options
    if @withcb
      @content=widgets.one_submit_with_cb("Invite a user using their email:", "Invite", "Can Post?")
    else
      @content=widgets.one_submit("Invite a user using their email:", "Invite")

  render: () =>
    @$el.html(@content)
    return this

  inviteUserEH: =>
    loc=window.location
    cback = (data) ->
            console.log "return data", data, loc
            window.location=location
    eback = (xhr, etext) ->
        console.log "ERROR", etext, loc
        #replace by a div alert from bootstrap
        alert "Did not succeed: #{etext}"
    console.log("GGG",@$el)
    #default for groups
    changerw=false
    if @withcb
      rwmode=@$('.cb').is(':checked')
      if rwmode
        changerw=true
      else
        changerw=false
    usernick=@$('.txt').val()
    syncs.invite_user("adsgut/user:#{usernick}", @postable, changerw, cback, eback)

class AddGroup extends Backbone.View

  tagName: 'div'

  events:
    "click .sub" : "addGroupEH"

  initialize: (options) ->
    {@withcb, @postable, @groups} = options
    if @withcb
      @content=widgets.dropdown_submit_with_cb(@groups,"Add a group you are a member of:","Add", "Can Post?")
    else
      @content=widgets.dropdown_submit(@groups,"Add a group you are a member of:","Add")

  render: () =>
    @$el.html(@content)
    return this

  addGroupEH: =>
    loc=window.location
    cback = (data) ->
            console.log "return data", data, loc
            window.location=location
    eback = (xhr, etext) ->
        console.log "ERROR", etext, loc
        #replace by a div alert from bootstrap
        alert "Did not succeed: #{etext}"
    console.log("GGG",@$el)
    #default for groups
    changerw=false
    if @withcb
      rwmode=@$('.cb').is(':checked')
      if rwmode
        changerw=true
      else
        changerw=false
    groupchosen=@$('.sel').val()
    console.log("GC", groupchosen)
    syncs.add_group(groupchosen, @postable, changerw, cback, eback)


root.get_tags = get_tags
root.get_taggings = get_taggings
root.format_items = format_items
root.format_tags = format_tags
root.get_groups= get_groups
root.format_stuff = format_stuff
root.views = 
  library_info: postable_info
  group_info: postable_info
  postable_inviteds: postable_inviteds
  InviteUser: InviteUser
  AddGroup: AddGroup
root.templates =
  library_info: library_info_template
  group_info: group_info_template
  postable_inviteds: postable_inviteds_template