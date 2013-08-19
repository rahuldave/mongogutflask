###
the idea behind syncs.coffee is to create a Backbone sync component for our API.
For this we must identify the models and views across our pages.

The method signature of Backbone.sync is sync(method, model, [options])

method – the CRUD method ("create", "read", "update", or "delete")
model – the model to be saved (or collection to be read)
options – success and error callbacks, and all other jQuery request options

With the default implementation, when Backbone.sync sends up a request to save a model, 
its attributes will be passed, serialized as JSON, and sent in the HTTP body with content-type application/json. 
When returning a JSON response, send down the attributes of the model that have been changed by the server, 
and need to be updated on the client. When responding to a "read" request from a collection (Collection#fetch), 
send down an array of model attribute objects.

Whenever a model or collection begins a sync with the server, a "request" event is emitted. 
If the request completes successfully you'll get a "sync" event, and an "error" event if not.

The sync function may be overriden globally as Backbone.sync, or at a finer-grained level, 
by adding a sync function to a Backbone collection or to an individual model.

#but we shall first start slow, by building in direct jquery functions here, instead of Backbone.sync.
This will document the api as well. We wont start with gets, but remember we want to later put gets inside
collections.fetch

error
Type: Function( jqXHR jqXHR, String textStatus, String errorThrown )
success
Type: Function( PlainObject data, String textStatus, jqXHR jqXHR )
###
root = exports ? this
$=jQuery
console.log "In Funcs"
h = teacup
doajax=$.ajax

#data={userthere, op}
accept_invitation = (nick, fqpn, cback, eback) ->
    url= "/postable/"+fqpn+"/doinvitation"
    data=
        userthere:nick
        op:'accept'
    params=
        type:'POST'
        dataType:'json'
        url:url
        data:JSON.stringify(data)
        contentType: "application/json"
        success:cback
        error:eback


    xhr=doajax(params)

invite_user = (nick, postable, changerw, cback, eback) ->
    console.log "in invite user", nick, postable, changerw
    url= "/postable/"+postable+"/doinvitation"
    data=
        userthere:nick
        op:'invite'
        changerw:changerw
    params=
        type:'POST'
        dataType:'json'
        url:url
        data:JSON.stringify(data)
        contentType: "application/json"
        success:cback
        error:eback
    xhr=doajax(params)

add_group = (selectedgrp, postable, changerw, cback, eback) ->
    console.log "SG", selectedgrp
    url= "/postable/"+postable+"/members"
    data=
        member:selectedgrp
        changerw:changerw
    params=
        type:'POST'
        dataType:'json'
        url:url
        data:JSON.stringify(data)
        contentType: "application/json"
        success:cback
        error:eback
    console.log data
    xhr=doajax(params)

root.syncs=
    accept_invitation: accept_invitation
    invite_user: invite_user
    add_group: add_group



