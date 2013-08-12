#we'll start with user profile funcs
root = exports ? this
$=jQuery
console.log "In Funcs"
h = teacup
w = widgets

parse_userinfo = (data) ->
    publ= "adsgut/group:public"
    priv= data.user.nick+"/group:default"
    postablesin=data.user.postablesin
    postablesowned=data.user.postablesowned
    postablesinvitedto=data.user.postablesinvitedto

    userdict=
        groupsin: (e.fqpn for e in postablesin when e.ptype is 'group' and e.fqpn not in [publ, priv])
        groupsowned: (e.fqpn for e in postablesowned when e.ptype is 'group' and e.fqpn not in [publ, priv])
        groupsinvitedto: (e.fqpn for e in postablesinvitedto when e.ptype is 'group')
        librariesin: (e.fqpn for e in postablesin when e.ptype is 'library')
        librariesowned: (e.fqpn for e in postablesowned when e.ptype is 'library')
        librariesinvitedto: (e.fqpn for e in postablesinvitedto when e.ptype is 'library')
        userinfo:
            nick: data.user.nick
            whenjoined: data.user.basic.whencreated
            name: data.user.basic.name
    return userdict

class Postable extends Backbone.Model

    initialize: (fqpn, invite=false)->
        @fqpn=fqpn
        @invite=invite

class PostableView extends Backbone.View

    tagName: "tr"

    initialize: (model)->
        console.log("v1")
        @model=model
        console?.log @model
       
    render: =>
        if @model.invite
            this.$(@el).html(w.table_from_dict_partial(@model.fqpn, 'X'))
        else
            content=w.one_col_table_partial(@model.fqpn)
            console?.log("fff", content)
            this.$(@el).html(content)
        return this



class PostableList extends Backbone.Collection
    
    model: Postable

    initialize: (fqpns, listtype, invite=false) ->
        console.log("m1")
        @listtype=listtype
        @invite=invite
        fqpnmods=(new Postable(p, invite) for p in fqpns)
        console.log fqpnmods
        @add(fqpnmods)

#BUG: do we not need to destroy when we move things around?
#also invite isnt enough to have the event based interplay between 2 lists
class PostableListView extends Backbone.View

    initialize: (coll, uniqel) ->
        console.log("h1")
        @collection=coll
        @el=$(uniqel)

    render: =>
        console.log "h2", @collection.models
        views=(new PostableView(m) for m in @collection.models)
        console.log "h3"
        if @collection.invite
            widget=w.table_from_dict("Invitations", "Accept?", (v.render().el for v in views), true)
        else
            widget=w.one_col_table(@collection.listtype, (v.render().el for v in views), true)
        this.$("div.#{@collection.listtype}").html(widget)


root.userprofile=
    parse_userinfo: parse_userinfo
    PostableList: PostableList
    PostableListView: PostableListView