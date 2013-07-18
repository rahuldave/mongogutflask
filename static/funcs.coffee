root = exports ? this
$=jQuery
console.log "In Filtera"

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


format_notes_for_item = (fqin, notes) ->
  t3list=("<span>#{t}</span><br/>" for t in notes[fqin])
  if t3list.length >0
    return "<p>Notes:<br/>"+t3list.join("<br/>")+"</p>"
  else
    return ""

format_tags_for_item = (fqin, stags, nick) ->
  t2list=("<a href=\"/postable/#{nick}/group:default/filter/html?query=tagname:#{t[0]}&query=tagtype:#{t[1]}\">#{t[0]}</a>" for t in stags[fqin])
  if t2list.length >0
    return "<span>Tagged as "+t2list.join(", ")+"</span>"
  else
    return ""

format_postings_for_item = (fqin, postings, nick) ->
  p2list=("<a href=\"/postable/#{p}/filter/html\">#{p}</a>" for p in postings[fqin] when p isnt "#{nick}/group:default")
  if p2list.length >0
    return "<span>Posted in "+p2list.join(", ")+"</span>"
  else
    return ""

format_items = ($sel, nick, items, count, stags, notes, postings, formatter, asform=false) ->
  adslocation="http://labs.adsabs.harvard.edu/adsabs/abs/"
  htmlstring=""
  for i in items
    fqin=i.basic.fqin
    url=adslocation+"#{i.basic.name}"
    htmlstring = htmlstring+"<#{formatter}><a href=\"#{url}\">#{i.basic.name}</a><br/>"
    htmlstring=htmlstring+format_tags_for_item(fqin, stags, nick)  
    htmlstring=htmlstring+format_postings_for_item(fqin, postings, nick) 
    htmlstring=htmlstring+format_notes_for_item(fqin, notes, nick)  
    htmlstring=htmlstring+"</#{formatter}>"
    if asform
      htmlstring=htmlstring+"<div class=\"control-group\">
                              <label class=\"control-label\">Add Note</label>
                              <input type=\"text\" class=\"controls\" placeholder=\"Type something…\">
                              <label class=\"checkbox control-label\">
                                <input type=\"checkbox\" class=\"controls\"> Make Private
                              </label>
                            </div>"

    $sel.prepend(htmlstring)
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

root.get_tags = get_tags
root.get_taggings = get_taggings
root.format_items = format_items
root.format_tags = format_tags