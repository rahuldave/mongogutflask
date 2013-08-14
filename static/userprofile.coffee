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


class PostableView extends Backbone.View

    tagName: "tr"
       
    render: =>

        if @model.get('invite')
            console.log "??", w.table_from_dict_partial(@model.get('fqpn'), 'X')
            @$el.html(w.table_from_dict_partial(@model.get('fqpn'), 'X'))
        else
            console.log '//'
            content=w.one_col_table_partial(@model.get('fqpn'))
            @$el.html(content)
        return this



class PostableList extends Backbone.Collection
    
    model: Postable

    initialize: (models, options) ->
        @listtype=options.listtype
        @invite=options.invite

#BUG: do we not need to destroy when we move things around?
#also invite isnt enough to have the event based interplay between 2 lists
class PostableListView extends Backbone.View
    tmap:
        in: "In"
        ow: "Owned"
        iv: "Invited"

    initialize: (options) ->
        @$el=options.$e_el

    render: =>
        console.log "h2", @collection
        views=(new PostableView(model:m) for m in @collection.models)
        console.log "h3", v.render().el for v in views
        if @collection.invite
            $widget=w.$table_from_dict("Invitations", "Accept?", (v.render().el for v in views))
        else
            $widget=w.$one_col_table(@tmap[@collection.listtype], (v.render().el for v in views))
        @$el.append($widget)


root.userprofile=
    parse_userinfo: parse_userinfo
    Postable: Postable
    PostableList: PostableList
    PostableListView: PostableListView