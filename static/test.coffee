Backbone=require('./backbone')

class Postable extends Backbone.Model

class PostableList extends Backbone.Collection
    
    initialize: (models, options) ->
        fqpnmods=(new Postable({fqpn:p}) for p in options.fqpns)
        @add(fqpnmods)
        console.log "BB", this.models
        return this

A=['a', 'b']
pl=new PostableList([],{fqpns:A})
console.log "GG", pl