from __future__ import with_statement

import os
import sys
import datetime
import flask
import simplejson

def todfo(ci):
    cijson=ci.to_json()
    cidict=simplejson.loads(cijson)
    return cidict

def todfl(cil):
    cijsonl=[e.to_json() for e in cil]
    cidictl=[simplejson.loads(e) for e in cijsonl]
    return cidictl

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../')))
#print "ATH", sys.path
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
     abort, render_template, flash, escape, make_response,  Blueprint

import datetime
from werkzeug import Response
from mongoengine import Document
from bson.objectid import ObjectId

class MongoEngineJsonEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Document):
            return obj.to_mongo()
        elif isinstance(obj, ObjectId):
            return unicode(obj)
        elif isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        try:
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return simplejson.JSONEncoder.default(self, obj)
 
def jsonify(*args, **kwargs):
    """ jsonify with support for MongoDB ObjectId
    """
    return Response(simplejson.dumps(dict(*args, **kwargs), cls=MongoEngineJsonEncoder), mimetype='application/json')
#BUG; these currently dont have doAborts
#do we need a dictpop? CHECK

#FOR GET
def _dictg(k,d, listmode=False):
    val=d.get(k, [None])
    if d.has_key(k):
        d.pop(k)
    if listmode:
        return val
    else:
        return val[0]

#FOR POST
def _dictp(k,d, default=None):
    val=d.get(k, default)
    if d.has_key(k):
        d.pop(k)
    return val

def _userpostget(g, postdict):
    nick=_dictp('useras', postdict)
    if nick:
        useras=g.db.getUserForNick(g.currentuser, nick)
    else:
        useras=g.currentuser
    return useras

def _userget(g, qdict):
    nick=_dictg('useras', qdict)
    userthere=_dictg('userthere', qdict)
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
    sortstring=_dictg('sort', qdict)
    if not sortstring:
        return None
    sort={}
    sort['field'], sort['ascending'] = sortstring.split(':')
    return sort

#criteria is a multiple ampersand list, with colon separators.
#eg criteria=basic__fqin:eq:something&criteria=
#we create from it a criteria list of dicts
def _criteriaget(qdict):
    #a serialixed dict of arbitrary keys, with mongo style encoding
    #later we will clamp down on it. BUG
    critlist=_dictg('criteria', qdict, True)
    if not critlist[0]:
        return False
    crit=[]
    for ele in critlist:
        cr={}
        cr['field'], cr['op'], cr['value'] = ele.split(':',2)
        crit.append(cr)
    return crit

def _queryget(qdict):
    #a serialixed dict of arbitrary keys, with mongo style encoding
    #later we will clamp down on it. BUG
    querylist=_dictg('query', qdict, True)
    if not querylist[0]:
        return {}
    q={}
    for ele in querylist:
        field, value = ele.split(':',1)
        if not q.has_key(field):
            q[field]=[]
        q[field].append(value)
    return q

def _pagtupleget(qdict):
    #a serialized tuple of offset, pagesize
    pagtuplestring=_dictg('pagtuple', qdict)
    if not pagtuplestring:
        return None
    plist=pagtuplestring.split(':')
    pagtuple=[int(e) if e else -1 for e in pagtuplestring.split(':')]
    return pagtuple

#currently force a new items each time.
def _itemsget(qdict):
    itemlist=_dictg('items', qdict, True)
    print "itemlist", itemlist
    if not itemlist[0]:
        return []
    #Possible security hole bug
    return itemlist

def _itemspostget(qdict):
    itemlist=_dictp('items', qdict)
    if not itemlist:
        return []
    #Possible security hole bug
    return itemlist

def _postablesget(qdict):
    plist=_dictp('postables', qdict)
    if not plist:
        return []
    #Possible security hole bug
    return plist

#used in POST, not in GET
def _itemstagsget(qdict):
    itemstagslist=_dictp('itemsandtags', qdict)
    if not itemstagslist:
        return []
    #Possible security hole bug
    return itemstagslist

#used in POST, not in get
def _tagspecsget(qdict):
    tagspecs=_dictp('tagspecs', qdict)
    if not tagspecs:
        return []
    #Possible security hole bug
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
    return jsonify(user=user)

#x
@adsgut.route('/user/<nick>/profile/html')
def userProfileHtml(nick):
    user=g.db.getUserInfo(g.currentuser, nick)
    return render_template('userprofile.html', theuser=user)

#x
@adsgut.route('/user/<nick>/groupsuserisin')
def groupsUserIsIn(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    groups=g.db.postablesForUser(g.currentuser, useras, "group")
    return jsonify(groups=groups)

#x
@adsgut.route('/user/<nick>/groupsuserowns')
def groupsUserOwns(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    groups=g.db.ownerOfPostables(g.currentuser, useras, "group")
    return jsonify(groups=groups)

#x
@adsgut.route('/user/<nick>/groupsuserisinvitedto')
def groupsUserIsInvitedTo(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    groups=g.db.postableInvitesForUser(g.currentuser, useras, "group")
    return jsonify(groups=groups)

#x
@adsgut.route('/user/<nick>/appsuserisin')
def appsUserIsIn(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    apps=g.db.postablesForUser(g.currentuser, useras, "app")
    return jsonify(apps=apps)

#x
@adsgut.route('/user/<nick>/appsuserowns')
def appsUserOwns(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    apps=g.db.ownerOfPostables(g.currentuser, useras, "app")
    return jsonify(apps=apps)

#use this for the email invitation?
#x
@adsgut.route('/user/<nick>/appsuserisinvitedto')
def appsUserIsInvitedTo(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    apps=g.db.postableInvitesForUser(g.currentuser, useras, "app")
    return jsonify(apps=apps)



@adsgut.route('/user/<nick>/librariesuserisin')
def librariesUserIsIn(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    libs=g.db.postablesForUser(g.currentuser, useras, "library")
    return jsonify(libraries=libs)

#x
@adsgut.route('/user/<nick>/librariesuserowns')
def librariesUserOwns(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    libs=g.db.ownerOfPostables(g.currentuser, useras, "library")
    return jsonify(libraries=libs)

#use this for the email invitation?
#x
@adsgut.route('/user/<nick>/librariesuserisinvitedto')
def librariesUserIsInvitedTo(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    libs=g.db.postableInvitesForUser(g.currentuser, useras, "library")
    return jsonify(libraries=libs)

#BUG currentuser useras here?
@adsgut.route('/user/<nick>/items')
def userItems(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    num, vals=g.dbp.getItemsForQuery(g.currentuser, useras,
       {'group':[useras.nick+"/group:default"]} )
    #userdict={'count':num, 'items':[simplejson.loads(v.to_json()) for v in vals]}
    return jsonify(count=num, items=vals)
#######################################################################################################################
#creating groups and apps
#accepting invites.
#DELETION methods not there BUG

#BUG: check currentuser useras stuff here
def createPostable(g, request, ptypestr):
    spec={}
    jsonpost=dict(request.json)
    useras=_userpostget(g,jsonpost)
    name=_dictp('name', jsonpost)
    if not name:
        doabort("BAD_REQ", "No Name Specified")
    description=_dictp('description', jsonpost, '')
    spec['creator']=useras.basic.fqin
    spec['name']=name
    spec['description']=description
    postable=g.db.addPostable(g.currentuser, useras, ptypestr, spec)
    return postable

@adsgut.route('/group', methods=['POST'])#groupname/description
def createGroup():
    if request.method == 'POST':
        newgroup=createPostable(g, request, "group")
        return jsonify(newgroup)
    else:
        doabort("BAD_REQ", "GET not supported")

@adsgut.route('/app', methods=['POST'])#name/description
def createApp():
    if request.method == 'POST':
        newapp=createPostable(g, request, "app")
        return jsonify(newapp)
    else:
        doabort("BAD_REQ", "GET not supported")

@adsgut.route('/library', methods=['POST'])#name/description
def createLibrary():
    if request.method == 'POST':
        newlibrary=createPostable(g, request, "library")
        return jsonify(newlibrary)
    else:
        doabort("BAD_REQ", "GET not supported")

@adsgut.route('/group/<groupowner>/group:<groupname>/doinvitation', methods=['POST'])#user/op
def doInviteToGroup(groupowner, groupname):
    #add permit to match user with groupowner
    fqgn=groupowner+"/group:"+groupname
    if request.method == 'POST':
        #specify your own nick for accept or decline
        jsonpost=dict(request.json)
        nick=_dictp('userthere', jsonpost)
        #for inviting this is nick of user invited. 
        #for accepting this is your own nick
        if not nick:
            doabort("BAD_REQ", "No User Specified")
        op=_dictp('op', jsonpost)
        if not op:
            doabort("BAD_REQ", "No Op Specified")
        if op=="invite":
            utba, p=g.db.inviteUserToPostableUsingNick(g.currentuser, fqgn, nick)
            return jsonify({'status':'OK', 'info': {'invited':utba.nick, 'to':fqgn}})
        elif op=='accept':
            me, p=g.db.acceptInviteToPostable(g.currentuser, fqgn, nick)
            return jsonify({'status':'OK', 'info': {'invited':me.nick, 'to': fqgn, 'accepted':True}})
        elif op=='decline':
            #BUG add something to invitations to mark declines.
            return jsonify({'status': 'OK', 'info': {'invited':nick, 'to': fqgn, 'accepted':False}})
        else:
            doabort("BAD_REQ", "No Op Specified")
    else:
        doabort("BAD_REQ", "GET not supported")

#BUG: user leakage as we do user info for all users in group. another users groups should not be obtainable
#BUG: should this handle a general memberable? must use a SHOWNFIELDS

#BUG: do we want a useras here? Also BUG:no existing version for tag, or POST to changer generable ownerable info yet
def addMemberToPostable(g, request, fqpn):
    jsonpost=dict(request.json)
    #BUG:need fqun right now. work with nicks later
    fqmn=_dictp('member', jsonpost)
    changerw=_dictp('changerw', jsonpost)
    if not changerw:
        changerw=False
    if not nick:
        doabort("BAD_REQ", "No User Specified")
    user, postable=g.db.addMemberableToPostable(g.currentuser, g.currentuser, fqpn, fqmn, changerw)
    return user, postable

def getMembersOfPostable(g, request, fqpn):
    useras=g.currentuser
    users=g.db.membersOfPostableFromFqin(g.currentuser,useras,fqpn)
    userdict={'users':users}
    return userdict

def getInvitedsForPostable(g, request, fqpn):
    useras=g.currentuser
    users=g.db.invitedsForPostableFromFqin(g.currentuser,useras,fqpn)
    userdict={'users':users}
    return userdict

@adsgut.route('/group/<groupowner>/group:<groupname>/inviteds')
def groupInviteds(groupowner, groupname):
    fqgn=groupowner+"/group:"+groupname
    userdict=getInvitedsForPostable(g, request, fqgn)
    return jsonify(userdict)

@adsgut.route('/group/<groupowner>/group:<groupname>/members', methods=['GET', 'POST'])#user
def addMembertoGroup_or_groupMembers(groupowner, groupname):
    #add permit to match user with groupowner
    fqgn=groupowner+"/group:"+groupname
    if request.method == 'POST':
        member, group=addMemberToPostable(g, request, fqgn)
        return jsonify({'status':'OK', 'info': {'member':member.basic.fqin, 'type':'group', 'postable':group.basic.fqin}})
    else:
        userdict=getMembersOfPostable(g, request, fqgn)
        return jsonify(userdict)

@adsgut.route('/app/<appowner>/app:<appname>/members', methods=['GET', 'POST'])#user
def addMemberToApp_or_appMembers(appowner, appname):
    #add permit to match user with groupowner
    fqan=appowner+"/app:"+appname
    if request.method == 'POST':
        member, app=addMemberToPostable(g, request, fqan)
        return jsonify({'status':'OK', 'info': {'member':member.basic.fqin, 'type':'app', 'postable':app.basic.fqin}})
    else:
        userdict=getMembersOfPostable(g, request, fqan)
        return jsonify(userdict)


@adsgut.route('/library/<libraryowner>/library:<libraryname>/members', methods=['GET', 'POST'])#user
def addMemberToLibrary_or_libraryMembers(libraryowner, libraryname):
    #add permit to match user with groupowner
    fqln=libraryowner+"/library:"+libraryname
    if request.method == 'POST':
        member, library=addMemberToPostable(g, request, fqln)
        return jsonify({'status':'OK', 'info': {'member':member.basic.fqin, 'type':'library', 'postable':library.basic.fqin}})
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
    return jsonify(group=postable(groupowner, groupname, "group"))

#x
@adsgut.route('/group/<groupowner>/group:<groupname>/profile/html')
def groupProfileHtml(groupowner, groupname):
    group=postable(groupowner, groupname, "group")
    return render_template('groupprofile.html', thegroup=group)

@adsgut.route('/group/<groupowner>/group:<groupname>/filter/html')
def groupFilterHtml(groupowner, groupname):
    querystring=request.query_string
    group=postable(groupowner, groupname, "group")
    return render_template('groupfilter.html', thegroup=group, querystring=querystring)

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
    return jsonify(app=postable(appowner, appname, "app"))

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
    return jsonify(library=postable(libraryowner, libraryname, "library"))

#x
@adsgut.route('/library/<libraryowner>/library:<libraryname>/profile/html')
def libraryProfileHtml(libraryowner, libraryname):
    library=postable(libraryowner, libraryname, "library")
    return render_template('libraryprofile.html', thelibrary=library)

@adsgut.route('/library/<libraryowner>/library:<libraryname>/filter/html')
def libraryFilterHtml(libraryowner, libraryname):
    querystring=request.query_string
    library=postable(libraryowner, libraryname, "library")
    return render_template('libraryfilter.html', thelibrary=library, querystring=querystring)


@adsgut.route('/postable/<po>/<pt>:<pn>/filter/html')
def postableFilterHtml(po, pt, pn):
    querystring=request.query_string
    p=postable(po, pn, pt)
    if pn=='default' and pt=='group':
        tqtype='stags'
    else:
        tqtype='tagname'
    tqtype='tagname'
    #BUG using currentuser right now. need to support a notion of useras
    return render_template('postablefilter.html', p=p, querystring=querystring, tqtype=tqtype, useras=g.currentuser)
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
    query=dict(request.args)
    useras, usernick=_userget(g, query)
    tagtype= _dictg('tagtype', query)
    #will not get notes
    stags=g.dbp.getTagsAsOwnerOnly(g.currentuser, useras, tagtype)
    stagdict={'simpletags':stags}
    return jsonify(stagdict)

#these are the simple tags user owns as well as can write to by dint of giving it to a group.
@adsgut.route('/user/<nick>/tagsusercanwriteto')
def tagsUserCanWriteTo(nick):
    query=dict(request.args)
    useras, usernick=_userget(g, query)
    tagtype= _dictg('tagtype', query)
    stags=g.dbp.getAllTagsForUser(g.currentuser, useras, tagtype)
    stagdict={'simpletags':stags}
    return jsonify(stagdict)

@adsgut.route('/user/<nick>/tagsasmember')
def tagsUserAsMember(nick):
    query=dict(request.args)
    useras, usernick=_userget(g, query)
    tagtype= _dictg('tagtype', query)
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
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        items = _itemspostget(jsonpost)

        fqpn=pns+"/"+ptype+":"+upname
        pds=[]
        for fqin in items:
            i,pd=g.dbp.postItemIntoPostable(g.currentuser, useras, fqpn, fqin)
            pds.append(pd)
        itempostings={'status':'OK', 'postings':pds, 'postable':fqpn}
        return jsonify(itempostings)
    else:
        query=dict(request.args)
        useras, usernick=_userget(g, query)
        print "QQQ",query, request.args
        #need to pop the other things like pagetuples etc. Helper funcs needed
        sort = _sortget(query)
        pagtuple = _pagtupleget(query)
        criteria= _criteriaget(query)
        postable= pns+"/"+ptype+":"+pname
        q=_queryget(query)
        print "Q is", q
        if not q.has_key('postables'):
            q['postables']=[]
        q['postables'].append(postable)
        
        #By this time query is popped down
        count, items=g.dbp.getItemsForQuery(g.currentuser, useras,
            q, usernick, criteria, sort, pagtuple)
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
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        itemsandtags = _itemstagsget(jsonpost)

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
        query=dict(request.args)
        useras, usernick=_userget(g, query)

        #need to pop the other things like pagetuples etc. Helper funcs needed
        sort = _sortget(query)
        criteria= _criteriaget(query)
        postable= pns+"/"+ptype+":"+pname
        q=_queryget(query)
        if not q.has_key('postables'):
            q['postables']=[]
        q['postables'].append(postable)
        #By this time query is popped down
        count, taggings=g.dbp.getTaggingsForQuery(g.currentuser, useras,
            q, usernick, criteria, sort)
        return jsonify({'taggings':taggings, 'count':count, 'postable':postable})

#GET all tags consistent with user for a particular postable and further query
#Why is this useful? And why tags from taggingdocs?
@adsgut.route('/postable/<pns>/<ptype>:<pname>/tags', methods=['GET'])
def tagsForPostable(pns, ptype, pname):
    #q={sort?, criteria?, postable}
    query=dict(request.args)
    useras, usernick=_userget(g, query)

    #need to pop the other things like pagetuples etc. Helper funcs needed
    #sort = _sortget(query)
    criteria= _criteriaget(query)
    postable= pns+"/"+ptype+":"+pname
    q=_queryget(query)
    if not q.has_key('postables'):
        q['postables']=[]
    q['postables'].append(postable)
    #By this time query is popped down
    count, tags=g.dbp.getTagsForQuery(g.currentuser, useras,
        q, usernick, criteria)
    return jsonify({'tags':tags, 'count':count})




#post saveItems(s), get could get various things such as stags, postings, and taggings
#get could take a bunch of items as arguments, or a query
@adsgut.route('/items', methods=['POST', 'GET'])
def items():
    ##useras?/name/itemtype
    #q={useras?, userthere?, sort?, pagetuple?, criteria?, stags|tagnames ?, postables?}
    if request.method=='POST':
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        itspec={}
        itspec['creator']=useras.basic.fqin
        itspec['name'] = _dictp('name', jsonpost)
        if not itspec['name']:
            doabort("BAD_REQ", "No name specified for item")
        itspec['itemtype'] = _dictp('itemtype', jsonpost)
        if not itspec['itemtype']:
            doabort("BAD_REQ", "No itemtype specified for item")
        newitem=g.dbp.saveItem(g.currentuser, useras, itspec)
        return jsonify({'status':'OK', 'info':newitem})
    else:
        query=dict(request.args)
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
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        tagspecs=_tagspecsget(jsonpost)
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
        query=dict(request.args)
        useras, usernick=_userget(g, query)

        #need to pop the other things like pagetuples etc. Helper funcs needed
        criteria= _criteriaget(query)
        #By this time query is popped down
        count, tags=g.dbp.getTagsForQuery(g.currentuser, useras,
            query, usernick, criteria)
        return jsonify({'tags':tags, 'count':count})

#GET tags for an item or POST: tagItem
#Currently GET coming from taggingdocs: BUG: not sure of this

def _setupTagspec(ti):
    #atleast one of name or content must be there (tag or note)
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
    return tagspec

@adsgut.route('/tags/<ns>/<itemname>', methods=['GET', 'POST'])
def tagsForItem(ns, itemname):
    #taginfos=[{tagname/tagtype/description}]
    #q=fieldlist=[('tagname',''), ('tagtype',''), ('context', None), ('fqin', None)]
    ifqin=ns+"/"+itemname
    if request.method == 'POST':
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        item=g.dbp._getItem(g.currentuser, ifqin)
        tagspecs=_tagspecsget(jsonpost)
        newtaggings=[]
        for ti in tagspecs:
            tagspec=_setupTagspec(ti)
            i,t,td=g.dbp.tagItem(g.currentuser, useras, item.basic.fqin, tagspec)
            newtaggings.append[td]

        #returning the taggings requires a commit at this point
        taggings={'status':'OK', 'info':{'item': i.basic.fqin, 'tagging':[td for td in newtaggings]}}
        return jsonify(taggings)
    else:
        print "REQUEST.args", request.args, dict(request.args)
        query=dict(request.args)
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
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        fqins = _itemspostget(jsonpost)
        tagspecs=_tagspecsget(jsonpost)
        newtaggings=[]
        for fqin in fqins:
            for ti in tagspecs:
                tagspec=_setupTagspec(ti)
                i,t,td=g.dbp.tagItem(g.currentuser, useras, fqin, tagspec)
                newtaggings.append[td]
        itemtaggings={'status':'OK', 'taggings':tds}
        return jsonify(itemtaggings)
    else:
        query=dict(request.args)
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
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        fqins = _itemspostget(jsonpost)
        fqpns = _postablesget(jsonpost)
        pds=[]
        for fqin in fqins:
            for fqpn in fqpns:
                i,pd=g.dbp.postItemIntoPostable(g.currentuser, useras, fqpn, fqin)
                pds.append(pd)
        itempostings={'status':'OK', 'postings':pds}
        return jsonify(itempostings)
    else:
        query=dict(request.args)
        useras, usernick=_userget(g, query)
        print 'QUERY', query
        #need to pop the other things like pagetuples etc. Helper funcs needed
        sort = _sortget(query)
        items = _itemsget(query)
        #By this time query is popped down
        postingsdict=g.dbp.getPostingsConsistentWithUserAndItems(g.currentuser, useras,
            items, sort)
        return jsonify(postingsdict)

@adsgut.route('/items/taggingsandpostings', methods=['POST', 'GET'])
def itemsTaggingsAndPostings():
    ##name/itemtype/uri/
    #q={useras?, sort?, items}
    if request.method=='POST':
        junk="NOT YET IMPLEMENTED AND I DONT THINK WE WILL"
    else:
        query=dict(request.args)
        useras, usernick=_userget(g, query)
        print 'AAAQUERY', query, request.args
        #need to pop the other things like pagetuples etc. Helper funcs needed
        sort = _sortget(query)
        items = _itemsget(query)
        #By this time query is popped down
        postingsdict=g.dbp.getPostingsConsistentWithUserAndItems(g.currentuser, useras,
            items, sort)
        taggingsdict=g.dbp.getTaggingsConsistentWithUserAndItems(g.currentuser, useras,
            items, sort)
        print taggingsdict, postingsdict
        return jsonify(postings=postingsdict, taggings=taggingsdict)

@adsgut.route('/itemtypes', methods=['POST', 'GET'])
def itemtypes():
    ##useras?/name/itemtype
    #q={useras?, userthere?, sort?, pagetuple?, criteria?, stags|tagnames ?, postables?}
    if request.method=='POST':
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        itspec={}
        itspec['creator']=useras.basic.fqin
        itspec['name'] = _dictp('name', jsonpost)
        if not itspec['name']:
            doabort("BAD_REQ", "No name specified for itemtype")
        itspec['postable'] = _dictp('postable', jsonpost)
        if not itspec['postable']:
            doabort("BAD_REQ", "No postable specified for itemtype")
        newitemtype=g.dbp.addItemType(g.currentuser, useras, itspec)
        return jsonify({'status':'OK', 'info':newitemtype})
    else:
        query=dict(request.args)
        useras, usernick=_userget(g, query)
        criteria= _criteriaget(query)
        isitemtype=True
        count, thetypes=g.dbp.getTypesForQuery(g.currentuser, useras, criteria, usernick, isitemtype)
        return jsonify({'types':thetypes, 'count':count})

#BUG: how to handle bools
@adsgut.route('/tagtypes', methods=['POST', 'GET'])
def tagtypes():
    ##useras?/name/itemtype
    #q={useras?, userthere?, sort?, pagetuple?, criteria?, stags|tagnames ?, postables?}
    if request.method=='POST':
        jsonpost=dict(request.json)
        useras = _userpostget(g, jsonpost)
        itspec={}
        itspec['creator']=useras.basic.fqin
        itspec['name'] = _dictp('name', jsonpost)
        itspec['tagmode'] = _dictp('tagmode', jsonpost)
        itspec['singletonmode'] = _dictp('singletonmode',jsonpost)
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
        itspec['postable'] = _dictp('postable', jsonpost)
        if not itspec['postable']:
            doabort("BAD_REQ", "No postable specified for itemtype")
        newtagtype=g.dbp.addTagType(g.currentuser, useras, itspec)
        return jsonify({'status':'OK', 'info':newtagtype})
    else:
        query=dict(request.args)
        useras, usernick=_userget(g, query)
        criteria= _criteriaget(query)
        isitemtype=False
        count, thetypes=g.dbp.getTypesForQuery(g.currentuser, useras, criteria, usernick, isitemtype)
        return jsonify({'types':thetypes, 'count':count})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)