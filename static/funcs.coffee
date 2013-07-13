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
    
    htmlstring = htmlstring+"<li><span><a href=\"#{url}\">#{k}</a>&nbsp;<a href=\"#{urla}\">(+)</a>#{v.join(',')}</span></li>"
  $sel.html(htmlstring)


format_items = ($sel, items, count, stags, notes, postings)->
  adslocation="http://labs.adsabs.harvard.edu/adsabs/abs/"
  htmlstring=""
  for i in items
    fqin=i.basic.fqin
    url=adslocation+"#{i.basic.name}"
    htmlstring = htmlstring+"<li><a href=\"#{url}\">#{i.basic.name}</a><br/>"
    t2list=("<a href=\"/postable/{{ useras.nick }}/group:default/filter/html?query=tagname:#{t[0]}&query=tagtype:#{t[1]}\">#{t[0]}</a>" for t in stags[fqin])
    htmlstring=htmlstring+"<span>Tagged as "+t2list.join(", ")+"</span>"
    t3list=("<span>#{t}</span><br/>" for t in notes[fqin])
    htmlstring=htmlstring+"<p>Notes:<br/>"+t3list.join("<br/>")+"</p>"
    p2list=("<a href=\"/postable/#{p}/filter/html\">#{p}</a>" for p in postings[fqin] when p isnt '{{ useras.nick }}/group:default')
    console.log "P@list", p2list
    htmlstring=htmlstring+"<span>Posted in "+p2list.join(", ")+"</span><br/></li>"

  $sel.html(htmlstring)
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