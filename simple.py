from __future__ import with_statement

import os
import sys
import datetime
import flask
import simplejson

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../')))
print "ATH", sys.path
from random import choice

from flask.ext.mongoengine import MongoEngine
from flask.ext.mongoengine.wtf import model_form
from flask_debugtoolbar import DebugToolbarExtension

app = flask.Flask(__name__)
app.config.from_object(__name__)
app.config['MONGODB_SETTINGS'] = {'DB': 'adsgut'}
app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'flask+mongoengine=<3'
app.debug = True
app.config['DEBUG_TB_PANELS'] = (
             'flask.ext.debugtoolbar.panels.versions.VersionDebugPanel',
             'flask.ext.debugtoolbar.panels.timer.TimerDebugPanel',
             'flask.ext.debugtoolbar.panels.headers.HeaderDebugPanel',
             'flask.ext.debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
             'flask.ext.debugtoolbar.panels.template.TemplateDebugPanel',
             'flask.ext.debugtoolbar.panels.logger.LoggingPanel',
             'flask.ext.mongoengine.panels.MongoDebugPanel'
             )

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

db = MongoEngine()
db.init_app(app)

DebugToolbarExtension(app)

from mongogut import itemsandtags

adsgut=app

from flask import request, session, g, redirect, url_for, \
     abort, render_template, flash, escape, make_response, jsonify, Blueprint

#BUG; these currently dont have doAborts
#do we need a dictpop? CHECK
def _dictp(k,d):
    val=d.get(k, None)
    if val:
        d.pop(k)
    return val

def _userget(g, qdict):
    nick=_dictp('useras', qdict)
    userthere=_dictp('userthere', qdict)
    if nick:
        useras=g.db.getUserForNick(g.currentuser, nick)
    else:
        useras=g.currentuser
    if userthere:
        usernick=useras.nick
    else:
        usernick=False
    return useras, usernick

def _sortget(qdict):
    #a serialixed dict of ascending and field
    sortstring=_dictp('sort', qdict)
    if not sortstring:
        return None
    sort=simplejson.loads(sortstring)
    return sort

def _criteriaget(qdict):
    #a serialixed dict of arbitrary keys, with mongo style encoding
    #later we will clamp down on it. BUG
    critstring=_dictp('criteria', qdict)
    if not critstring:
        return False
    crit=simplejson.loads(critstring)
    return crit

def _pagtupleget(qdict):
    #a serialized tuple of offset, pagesize
    pagtuplestring=_dictp('pagtuple', qdict)
    if not pagtuplestring:
        return None
    pagtuple=simplejson.loads(pagtuplestring)
    return pagtuple

def _itemsget(qdict):
    #a serialixed dict of ascending and field
    itemstring=_dictp('items', qdict)
    if not itemstring:
        return []
    #Possible security hole bug
    items=simplejson.loads(itemstring)
    return items

def _itemstagsget(qdict):
    #a serialixed dict of ascending and field
    itemtagstring=_dictp('itemsandtags', qdict)

    if not itemtagstring:
        return []
    #Possible security hole bug
    itemsandtags=simplejson.loads(itemtagstring)
    return itemsandtags

def _tagspecsget(qdict):
    #a serialixed dict of ascending and field
    tagspecstring=_dictp('tagspecs', qdict)
    if not tagspecstring:
        return []
    #Possible security hole bug
    tagspecs=simplejson.loads(tagspecstring)
    return tagspecs

#x
@adsgut.before_request
def before_request():
    username=session.get('username', None)
    print "USER", username
    p=itemsandtags.Postdb(db)
    w=p.whosdb
    g.db=w
    g.dbp=p
    if not username:
        username='adsgut'
    #superuser if no login BUG: use only for testing

    #currently set to sysuser. Atherwise have user login and set.
    g.currentuser=g.db.getUserForNick(None, username)


@adsgut.route('/login', methods=['GET', 'POST'])
def login():
    error=None
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['logged_in'] = True
        flash('You were logged in')
        return redirect(url_for('index'))
    return render_template('login.html', error=error)

@adsgut.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))


#x
@adsgut.route('/')
def index():
    return "Hello World"
#x
@adsgut.route('/all')
def all():
    groups=g.db.allGroups(g.currentuser)
    apps=g.db.allApps(g.currentuser)
    libraries=g.db.allLibraries(g.currentuser)
    users=g.db.allUsers(g.currentuser)
    return flask.render_template('index.html', groups=groups, apps=apps, users=users, libraries=libraries)

#######################################################################################################################
#######################################################################################################################

#Information about users, groups, and apps
#TODO: should we support a modicum of user information for others
#like group and app owners?
#x
@adsgut.route('/user/<nick>')
def userInfo(nick):
    user=g.db.getUserInfo(g.currentuser, nick)
    return user.to_json()

#x
@adsgut.route('/user/<nick>/profile/html')
def userProfileHtml(nick):
    useras=userInfo(nick)
    return render_template('userprofile.html', theuser=simplejson.loads(useras))

#x
@adsgut.route('/user/<nick>/groupsuserisin')
def groupsUserIsIn(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    groups=g.db.postablesForUser(g.currentuser, useras, "group")
    groupdict={'groups':groups}
    return jsonify(groupdict)

#x
@adsgut.route('/user/<nick>/groupsuserowns')
def groupsUserOwns(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    groups=g.db.ownerOfPostables(g.currentuser, useras, "group")
    groupdict={'groups':groups}
    return jsonify(groupdict)

#x
@adsgut.route('/user/<nick>/groupsuserisinvitedto')
def groupsUserIsInvitedTo(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    groups=g.db.postableInvitesForUser(g.currentuser, useras, "group")
    groupdict={'groups':groups}
    return jsonify(groupdict)

#x
@adsgut.route('/user/<nick>/appsuserisin')
def appsUserIsIn(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    apps=g.db.postablesForUser(g.currentuser, useras, "app")
    appdict={'apps':apps}
    return jsonify(appdict)

#x
@adsgut.route('/user/<nick>/appsuserowns')
def appsUserOwns(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    apps=g.db.ownerOfPostables(g.currentuser, useras, "app")
    appdict={'apps':apps}
    return jsonify(appdict)

#use this for the email invitation?
#x
@adsgut.route('/user/<nick>/appsuserisinvitedto')
def appsUserIsInvitedTo(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    apps=g.db.postableInvitesForUser(g.currentuser, useras, "app")
    appdict={'apps':apps}
    return jsonify(appdict)



@adsgut.route('/user/<nick>/librariesuserisin')
def librariesUserIsIn(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    libs=g.db.postablesForUser(g.currentuser, useras, "library")
    libdict={'libraries':libs}
    return jsonify(libdict)

#x
@adsgut.route('/user/<nick>/librariesuserowns')
def librariesUserOwns(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    libs=g.db.ownerOfPostables(g.currentuser, useras, "library")
    libdict={'libraries':libs}
    return jsonify(libdict)

#use this for the email invitation?
#x
@adsgut.route('/user/<nick>/librariesuserisinvitedto')
def librariesUserIsInvitedTo(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    libs=g.db.postableInvitesForUser(g.currentuser, useras, "library")
    libdict={'libraries':libs}
    return jsonify(libdict)

@adsgut.route('/user/<nick>/items')
def userItems(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    num, vals=g.dbp.getItemsForQuery(g.currentuser, useras,
       {'group':[useras.nick+"/group:default"]} )
    userdict={'count':num, 'items':[simplejson.loads(v.to_json()) for v in vals]}
    return jsonify(userdict)
#######################################################################################################################
#creating groups and apps
#accepting invites.
#DELETION methods not there BUG

def createPostable(g, request, ptypestr):
    user=g.currentuser
    spec={}
    name=request.form.get('name', None)
    if not name:
        doabort("BAD_REQ", "No Name Specified")
    description=request.form.get('description', '')
    spec['creator']=user.basic.fqin
    spec['name']=name
    spec['description']=description
    postable=g.db.addPostable(user, user, ptypestr, spec)
    return postable

@adsgut.route('/group', methods=['POST'])#groupname/description
def createGroup():
    if request.method == 'POST':
        newgroup=createPostable(g, request, "group")
        return newgroup.to_json()
    else:
        doabort("BAD_REQ", "GET not supported")

@adsgut.route('/app', methods=['POST'])#name/description
def createApp():
    if request.method == 'POST':
        newapp=createPostable(g, request, "app")
        return newapp.to_json()
    else:
        doabort("BAD_REQ", "GET not supported")

@adsgut.route('/library', methods=['POST'])#name/description
def createLibrary():
    if request.method == 'POST':
        newlibrary=createPostable(g, request, "library")
        return newlibrary.to_json()
    else:
        doabort("BAD_REQ", "GET not supported")

@adsgut.route('/group/<groupowner>/group:<groupname>/doinvitation', methods=['POST'])#user/op
def doInviteToGroup(groupowner, groupname):
    #add permit to match user with groupowner
    fqgn=groupowner+"/group:"+groupname
    if request.method == 'POST':
        #specify your own nick for accept or decline
        nick=request.form.get('userthere', None)
        if not nick:
            doabort("BAD_REQ", "No User Specified")
        op=request.form.get('op', None)
        if not op:
            doabort("BAD_REQ", "No Op Specified")
        if op=="invite":
            usertobeadded=g.db.getUserForNick(g.currentuser, nick)
            g.db.inviteUserToGroup(g.currentuser, fqgn, usertobeadded)
            return jsonify({'status':'OK', 'info': {'invited':nick, 'to':fqgn}})
        elif op=='accept':
            g.db.acceptInviteToGroup(g.currentuser, fqgn, userinvited)
            return jsonify({'status':'OK', 'info': {'invited':nick, 'to': fqgn, 'accepted':True}})
        elif op=='decline':
            #BUG add something to invitations to mark declines.
            return jsonify({'status': 'OK', 'info': {'invited':nick, 'to': fqgn, 'accepted':False}})
        else:
            doabort("BAD_REQ", "No Op Specified")
    else:
        doabort("BAD_REQ", "GET not supported")

#BUG: user leakage as we do user info for all users in group. another users groups should not be obtainable
#BUG: should this handle a general memberable? must use a SHOWNFIELDS

def addMemberToPostable(g, request, fqpn):
    nick=request.form.get('userthere', None)
    if not nick:
        doabort("BAD_REQ", "No User Specified")
    user, postable=g.db.addUserToPostable(g.currentuser, fqpn, nick)
    return user, postable

def getMembersOfPostable(g, request, fqpn):
    useras=g.currentuser
    users=g.db.membersOfPostableFromFqin(g.currentuser,useras,fqpn)
    userdict={'users':users}
    return userdict

@adsgut.route('/group/<groupowner>/group:<groupname>/members', methods=['GET', 'POST'])#user
def addMembertoGroup_or_groupMembers(groupowner, groupname):
    #add permit to match user with groupowner
    fqgn=groupowner+"/group:"+groupname
    if request.method == 'POST':
        user, group=addMemberToPostable(g, request, fqgn)
        return jsonify({'status':'OK', 'info': {'user':user.nick, 'type':'group', 'postable':group.basic.fqin}})
    else:
        userdict=getMembersOfPostable(g, request, fqgn)
        return jsonify(userdict)

@adsgut.route('/app/<appowner>/app:<appname>/members', methods=['GET', 'POST'])#user
def addMemberToApp_or_appMembers(appowner, appname):
    #add permit to match user with groupowner
    fqan=appowner+"/app:"+appname
    if request.method == 'POST':
        user, app=addMemberToPostable(g, request, fqan)
        return jsonify({'status':'OK', 'info': {'user':user.nick, 'type':'app', 'postable':app.basic.fqin}})
    else:
        userdict=getMembersOfPostable(g, request, fqan)
        return jsonify(userdict)


@adsgut.route('/library/<libraryowner>/library:<libraryname>/members', methods=['GET', 'POST'])#user
def addMemberToLibrary_or_libraryMembers(libraryowner, libraryname):
    #add permit to match user with groupowner
    fqln=libraryowner+"/library:"+libraryname
    if request.method == 'POST':
        user, library=addMemberToPostable(g, request, fqln)
        return jsonify({'status':'OK', 'info': {'user':user.nick, 'type':'library', 'postable':library.basic.fqin}})
    else:
        userdict=getMembersOfPostable(g, request, fqln)
        return jsonify(userdict)

#######################################################################################################################
#######################################################################################################################
def postable(ownernick, name, ptypestr):
    fqpn=ownernick+"/"+ptypestr+":"+name
    postable=g.db.getPostable(g.currentuser, fqpn)
    return postable


#POST/GET in a lightbox?
@adsgut.route('/group/html')
def creategrouphtml():
    pass

#get group info
#x
@adsgut.route('/group/<groupowner>/group:<groupname>')
def groupInfo(groupowner, groupname):
    return postable(groupowner, groupname, "group").to_json()

#x
@adsgut.route('/group/<groupowner>/group:<groupname>/profile/html')
def groupProfileHtml(groupowner, groupname):
    group=postable(groupowner, groupname, "group")
    return render_template('groupprofile.html', thegroup=group)

# @adsgut.route('/group/<groupowner>/group:<groupname>/items')
# def groupItems(groupowner, groupname):
#     group=postable(groupowner, groupname, "group")
#     num, vals=g.dbp.getItemsForQuery(g.currentuser, g.currentuser,
#        {'postables':[group.basic.fqin]} )
#     groupdict={'count':num, 'items':[simplejson.loads(v.to_json()) for v in vals]}
#     return jsonify(groupdict)
#######################################################################################################################
#######################################################################################################################

#POST/GET in a lightbox?
@adsgut.route('/app/html')
def createapphtml():
    pass

#x
@adsgut.route('/app/<appowner>/app:<appname>')
def appInfo(appowner, appname):
    return postable(appowner, appname, "app").to_json()

#x
@adsgut.route('/app/<appowner>/app:<appname>/profile/html')
def appProfileHtml(appowner, appname):
    app=postable(appowner, appname, "app")
    return render_template('appprofile.html', theapp=app)

# @adsgut.route('/app/<appowner>/app:<appname>/items')
# def appItems(appowner, appname):
#     app=postable(appowner, appname, "app")
#     num, vals=g.dbp.getItemsForQuery(g.currentuser, g.currentuser,
#        {'postables':[app.basic.fqin]} )
#     appdict={'count':num, 'items':[simplejson.loads(v.to_json()) for v in vals]}
#     return jsonify(appdict)
#######################################################################################################################
#######################################################################################################################
#POST/GET in a lightbox?
@adsgut.route('/library/html')
def createlibraryhtml():
    pass

#get group info
#x
@adsgut.route('/library/<libraryowner>/library:<libraryname>')
def libraryInfo(libraryowner, libraryname):
    return postable(libraryowner, libraryname, "library").to_json()

#x
@adsgut.route('/library/<libraryowner>/library:<libraryname>/profile/html')
def libraryProfileHtml(libraryowner, libraryname):
    library=postable(libraryowner, libraryname, "library")
    return render_template('libraryprofile.html', thelibrary=library)

# @adsgut.route('/library/<libraryowner>/library:<libraryname>/items')
# def libraryItems(libraryowner, libraryname):
#     library=postable(libraryowner, libraryname, "library")
#     num, vals=g.dbp.getItemsForQuery(g.currentuser, g.currentuser,
#        {'postables':[library.basic.fqin]} )
#     libdict={'count':num, 'items':[simplejson.loads(v.to_json()) for v in vals]}
#     return jsonify(libdict)

#######################################################################################################################
#######################################################################################################################

def _getContext(q):
    #BUG:user contexts will be hidden. So this will change
    if not q.has_key('cuser'):
        return None
    context={}
    if q['cuser']=="True":
        context['user']=True
    else:
        context['user']=False
    if not q.has_key('ctype'):
        return None
    context['type']=q['ctype']
    if not q.has_key('cvalue'):
        return None
    context['value']=q['cvalue']
    return context



#these might be supersed by tagging based results to populate the left side

#The users simple tags, not singletonmode (ie no notes), not libraries
@adsgut.route('/user/<nick>/tagsuserowns')
def tagsUserOwns(nick):
    query=request.args
    useras, usernick=_userget(g, query)
    tagtype= _dictp('tagtype', query)
    #will not get notes
    stags=g.dbp.getTagsAsOwnerOnly(g.currentuser, useras, tagtype)
    stagdict={'simpletags':stags}
    return jsonify(stagdict)

#these are the simple tags user owns as well as can write to by dint of giving it to a group.
@adsgut.route('/user/<nick>/tagsusercanwriteto')
def tagsUserCanWriteTo(nick):
    query=request.args
    useras, usernick=_userget(g, query)
    tagtype= _dictp('tagtype', query)
    stags=g.dbp.getAllTagsForUser(g.currentuser, useras, tagtype)
    stagdict={'simpletags':stags}
    return jsonify(stagdict)

@adsgut.route('/user/<nick>/tagsasmember')
def tagsUserAsMember(nick):
    query=request.args
    useras, usernick=_userget(g, query)
    tagtype= _dictp('tagtype', query)
    stags=g.dbp.getTagsAsMemberOnly(g.currentuser, useras, tagtype)
    stagdict={'simpletags':stags}
    return jsonify(stagdict)

########################


#################now going to tags and posts#################################

#above 3 stags will be superseded, rolled in
#BUG: no multis are done for now.


#POST posts items into postable, get gets items for postable consistent with user.
@adsgut.route('/postable/<pns>/<ptype>:<pname>/items', methods=['GET', 'POST'])
def itemsForPostable(pns, ptype, pname):
    #userthere/[fqins]
    #q={sort?, pagtuple?, criteria?, postable}
    if request.method=='POST':
        useras, usernick=_userget(g, request.form)
        items = _itemsget(query)

        fqpn=pns+"/"+ptype+":"+upname
        pds=[]
        for fqin in items:
            i,pd=g.dbp.postItemIntoPostable(g.currentuser, useras, fqpn, fqin)
            pds.append(pd)
        itempostings={'status':'OK', 'postings':pds, 'postable':fqpn}
        return jsonify(itempostings)
    else:
        query=request.args
        useras, usernick=_userget(g, query)

        #need to pop the other things like pagetuples etc. Helper funcs needed
        sort = _sortget(query)
        pagtuple = _pagtupleget(query)
        criteria= _criteriaget(query)
        postable= pns+"/"+ptype+":"+pname
        #By this time query is popped down
        count, items=g.dbp.getItemsForQuery(g.currentuser, useras,
            {'postables':[postable]}, usernick, criteria, sort, pagtuple)
        return jsonify({'items':items, 'count':count, 'postable':postable})

@adsgut.route('/library/<libraryowner>/library:<libraryname>/items')
def libraryItems(libraryowner, libraryname):
    return itemsForPostable(libraryowner, "library", libraryname)

@adsgut.route('/app/<appowner>/app:<appname>/items')
def appItems(appowner, appname):
    return itemsForPostable(appowner, "app", appname)

@adsgut.route('/group/<groupowner>/group:<groupname>/items')
def groupItems(groupowner, groupname):
    return itemsForPostable(groupowner, "group", groupname)

#For the RHS, given a set of items. Should this even be exposed as such?
#we need it for post, but goes the GET make any sense?
#CHECK: and is it secure?
#this is post tagging into postable for POST

@adsgut.route('/postable/<pns>/<ptype>:<pname>/taggings', methods=['GET', 'POST'])
def taggingsForPostable(pns, ptype, pname):
    #userthere/fqin/fqtn
    #q={sort?, criteria?, postable}
    if request.method=='POST':
        useras, usernick=_userget(g, request.form)
        itemsandtags = _itemsget(query)

        fqpn=pns+"/"+ptype+":"+upname
        tds=[]
        for d in itemsandtags:
            fqin=d['fqin']
            fqtn=d['fgtn']
            td=g.dbp.getTaggingDoc(g.currentuser, useras, fqin, fqtn)
            i,t,td=g.dbp.postTaggingIntoPostable(g.currentuser, useras, fqpn, td)
            tds.append(td)
        itemtaggings={'status':'OK', 'taggings':tds, 'postable':fqpn}
        return jsonify(itemtaggings)
    else:
        query=request.args
        useras, usernick=_userget(g, query)

        #need to pop the other things like pagetuples etc. Helper funcs needed
        sort = _sortget(query)
        criteria= _criteriaget(query)
        postable= pns+"/"+ptype+":"+pname
        #By this time query is popped down
        count, taggings=g.dbp.getTaggingsForQuery(g.currentuser, useras,
            {'postables':[postable]}, usernick, criteria, sort)
        return jsonify({'taggings':taggings, 'count':count, 'postable':postable})

#GET all tags consistent with user for a particular postable and further query
#Why is this useful? And why tags from taggingdocs?
@adsgut.route('/postable/<pns>/<ptype>:<pname>/tags', methods=['GET'])
def tagsForPostable(pns, ptype, pname):
    #q={sort?, criteria?, postable}
    query=request.args
    useras, usernick=_userget(g, query)

    #need to pop the other things like pagetuples etc. Helper funcs needed
    sort = _sortget(query)
    criteria= _criteriaget(query)
    postable= pns+"/"+ptype+":"+pname
    #By this time query is popped down
    count, tags=g.dbp.getTagsForQuery(g.currentuser, useras,
        {'postables':[postable]}, usernick, criteria, sort)
    return jsonify({'tags':tags, 'count':count})




#post saveItems(s), get could get various things such as stags, postings, and taggings
#get could take a bunch of items as arguments, or a query
@adsgut.route('/items', methods=['POST', 'GET'])
def items():
    ##useras?/name/itemtype
    #q={useras?, userthere?, sort?, pagetuple?, criteria?, stags|tagnames ?, postables?}
    if request.method=='POST':
        useras, usernick=_userget(g, request.form)
        itspec={}
        itspec['creator']=useras.basic.fqin
        itspec['name'] = request.form.get('name', None)
        if not itspec['name']:
            doabort("BAD_REQ", "No name specified for item")
        itspec['itemtype'] = request.form.get('itemtype', None)
        if not itspec['itemtype']:
            doabort("BAD_REQ", "No itemtype specified for item")
        newitem=g.dbp.saveItem(g.currentuser, useras, itspec)
        return jsonify({'status':'OK', 'info':newitem})
    else:
        query=request.args
        useras, usernick=_userget(g, query)

        #need to pop the other things like pagetuples etc. Helper funcs needed
        sort = _sortget(query)
        pagtuple = _pagtupleget(query)
        criteria= _criteriaget(query)
        #By this time query is popped down
        count, items=g.dbp.getItemsForQuery(g.currentuser, useras,
            query, usernick, criteria, sort, pagtuple)
        return jsonify({'items':items, 'count':count})

#Get tags for a query. We can use post to just create a new tag. [NOT TO DO TAGGING]
#This is as opposed to tagging an item and would be used in biblio apps and such.
#CHECK: currently get coming from taggingdocs. Not sure about this
#BUG: we should make sure it only allows name based tags
#Will let you create multiple tags
#GET again comes from taggingdocs. Why?
@adsgut.route('/tags', methods=['POST', 'GET'])
def tags():
    ##useras?/name/itemtype
    #q={useras?, userthere?, sort?, pagetuple?, criteria?, stags|tagnames ?, postables?}
    if request.method=='POST':
        useras, usernick=_userget(g, request.form)
        tagspecs=_tagspecsget(request.form)
        newtags=[]
        for ti in tagspecs:
            if not ti.has_key('name'):
                doabort('BAD_REQ', "No name specified for tag")
            if not ti.has_key('tagtype'):
                doabort('BAD_REQ', "No tagtypes specified for tag")
            tagspec={}
            tagspec['creator']=useras.basic.fqin
            if ti.has_key('name'):
                tagspec['name'] = ti['name']
            tagspec['tagtype'] = ti['tagtype']
            t=g.dbp.makeTag(g.currentuser, useras, tagspec)
            newtags.append[t]

        #returning the taggings requires a commit at this point
        tags={'status':'OK', 'info':{'item': i.basic.fqin, 'tags':[td for td in newtags]}}
        return jsonify(tags)
    else:
        query=request.args
        useras, usernick=_userget(g, query)

        #need to pop the other things like pagetuples etc. Helper funcs needed
        sort = _sortget(query)
        criteria= _criteriaget(query)
        #By this time query is popped down
        count, tags=g.dbp.getTagsForQuery(g.currentuser, useras,
            query, usernick, criteria, sort)
        return jsonify({'tags':tags, 'count':count})

#GET tags for an item or POST: tagItem
#Currently GET coming from taggingdocs: BUG: not sure of this
@adsgut.route('/tags/<ns>/<itemname>', methods=['GET', 'POST'])
def tagsForItem(ns, itemname):
    #taginfos=[{tagname/tagtype/description}]
    #q=fieldlist=[('tagname',''), ('tagtype',''), ('context', None), ('fqin', None)]
    ifqin=ns+"/"+itemname
    if request.method == 'POST':
        useras, usernick=_userget(g, request.form)
        item=g.dbp._getItem(g.currentuser, ifqin)
        tagspecs=_tagspecsget(request.form)
        newtaggings=[]
        for ti in tagspecs:
            if not (ti.has_key('name') or ti.has_key('content')):
                doabort('BAD_REQ', "No name or content specified for tag")
            if not ti['tagtype']:
                doabort('BAD_REQ', "No tagtypes specified for tag")
            tagspec={}
            tagspec['creator']=useras.basic.fqin
            if ti.has_key('name'):
                tagspec['name'] = ti['name']
            if ti.has_key('content'):
                tagspec['content'] = ti['content']
            tagspec['tagtype'] = ti['tagtype']
            i,t,td=g.dbp.tagItem(g.currentuser, useras, item.basic.fqin, tagspec)
            newtaggings.append[td]

        #returning the taggings requires a commit at this point
        taggings={'status':'OK', 'info':{'item': i.basic.fqin, 'tagging':[td for td in newtaggings]}}
        return jsonify(taggings)
    else:
        query=request.args
        useras, usernick=_userget(g, query)

        #need to pop the other things like pagetuples etc. Helper funcs needed
        sort = _sortget(query)

        #By this time query is popped down
        #I am not convinced this is how to do this query
        # criteria= _criteriaget(query)
        # criteria.append(['field':'thething__thingtopostfqin', 'op':'eq', 'value':ifqin])
        # count, tags=g.dbp.getTagsForQuery(g.currentuser, useras,
        #     query, usernick, criteria, sort)
        count, tags= g.dbp.getTagsConsistentWithUserAndItems(g.currentuser, useras, [ifqin], sort)
        return jsonify({'tags':tags, 'count':count})
####These are the fromSpec family of functions for GET

#multi item multi tag tagging on POST and get taggings
@adsgut.route('/items/taggings', methods=['POST', 'GET'])
def itemsTaggings():
    ##name/itemtype/uri/
    #q={useras?, sort?, items}
    if request.method=='POST':
        junk="NOT YET IMPLEMENTED"
    else:
        query=request.args
        useras, usernick=_userget(g, query)

        #need to pop the other things like pagetuples etc. Helper funcs needed
        sort = _sortget(query)
        items = _itemsget(query)
        #By this time query is popped down
        taggingsdict=g.dbp.getTaggingsConsistentWithUserAndItems(g.currentuser, useras,
            items, sort)
        return jsonify(taggingsdict)

#multi item multi postable posting on POST and get posts
@adsgut.route('/items/postings', methods=['POST', 'GET'])
def itemsPostings():
    ##name/itemtype/uri/
    #q={useras?, sort?, items}
    if request.method=='POST':
        junk="NOT YET IMPLEMENTED"
    else:
        query=request.args
        useras, usernick=_userget(g, query)

        #need to pop the other things like pagetuples etc. Helper funcs needed
        sort = _sortget(query)
        items = _itemsget(query)
        #By this time query is popped down
        postingsdict==g.dbp.getPostingsConsistentWithUserAndItems(g.currentuser, useras,
            items, sort)
        return jsonify(postingsdict)

@adsgut.route('/itemtypes', methods=['POST', 'GET'])
def itemtypes():
    ##useras?/name/itemtype
    #q={useras?, userthere?, sort?, pagetuple?, criteria?, stags|tagnames ?, postables?}
    if request.method=='POST':
        useras, usernick=_userget(g, request.form)
        itspec={}
        itspec['creator']=useras.basic.fqin
        itspec['name'] = request.form.get('name', None)
        if not itspec['name']:
            doabort("BAD_REQ", "No name specified for itemtype")
        itspec['postable'] = request.form.get('postable', None)
        if not itspec['postable']:
            doabort("BAD_REQ", "No postable specified for itemtype")
        newitemtype=g.dbp.addItemType(g.currentuser, useras, itspec)
        return jsonify({'status':'OK', 'info':newitemtype})
    else:
        query=request.args
        useras, usernick=_userget(g, query)
        criteria= _criteriaget(query)
        isitemtype=True
        count, thetypes=g.dbp.getTypesForQuery(currentuser, useras, criteria, usernick, isitemtype)
        return jsonify({'types':thetypes, 'count':count})

#BUG: how to handle bools
@adsgut.route('/tagtypes', methods=['POST', 'GET'])
def tagtypes():
    ##useras?/name/itemtype
    #q={useras?, userthere?, sort?, pagetuple?, criteria?, stags|tagnames ?, postables?}
    if request.method=='POST':
        useras, usernick=_userget(g, request.form)
        itspec={}
        itspec['creator']=useras.basic.fqin
        itspec['name'] = request.form.get('name', None)
        itspec['tagmode'] = request.form.get('tagmode', None)
        itspec['singletonmode'] = request.form.get('singletonmode', None)
        if not itspec['tagmode']:
            del itspec['tagmode']
        else:
            itspec['tagmode']=bool(itspec['tagmode'])
        if not itspec['singletonmode']:
            del itspec['singletonmode']
         else:
            itspec['singletonmode']=bool(itspec['singletonmode'])
        if not itspec['name']:
            doabort("BAD_REQ", "No name specified for itemtype")
        itspec['postable'] = request.form.get('postable', None)
        if not itspec['postable']:
            doabort("BAD_REQ", "No postable specified for itemtype")
        newtagtype=g.dbp.addTagType(g.currentuser, useras, itspec)
        return jsonify({'status':'OK', 'info':newtagtype})
    else:
        query=request.args
        useras, usernick=_userget(g, query)
        criteria= _criteriaget(query)
        isitemtype=False
        count, thetypes=g.dbp.getTypesForQuery(currentuser, useras, criteria, usernick, isitemtype)
        return jsonify({'types':thetypes, 'count':count})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)