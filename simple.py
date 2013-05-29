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
    num, vals=g.dbp.getItemsForPostableQuery(g.currentuser, useras,
       [useras.nick+"/group:default"] )
    userdict={'count':num, 'items':[simplejson.loads(v.to_json()) for v in vals]}
    return jsonify(userdict)
#######################################################################################################################
#creating groups and apps
#accepting invites.
#DELETION methods not there BUG

@adsgut.route('/group', methods=['POST'])#groupname/description
def createGroup():
    user=g.currentuser
    groupspec={}
    if request.method == 'POST':
        groupname=request.form.get('name', None)
        if not groupname:
            doabort("BAD_REQ", "No Group Specified")
        description=request.form.get('description', '')
        groupspec['creator']=user
        groupspec['name']=groupname
        groupspec['description']=description
        newgroup=g.db.addGroup(g.currentuser, user, groupspec)
        return newgroup.to_json()
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

#This is used for addition of a user. Whats the usecase? current perms protect this
#TODO: maybe add a bulk version? That would seem to need to be added as a pythonic API: also split there into two things in pythonic API?
#BUG: user leakage as we do user info for all users in group. another users groups should not be obtainable
#BUG: should this handle a general memberable?
@adsgut.route('/group/<groupowner>/group:<groupname>/members', methods=['GET', 'POST'])#user
def addMembertoGroup_or_groupMembers(groupowner, groupname):
    #add permit to match user with groupowner
    fqgn=groupowner+"/group:"+groupname
    if request.method == 'POST':
        nick=request.form.get('userthere', None)
        if not nick:
            doabort("BAD_REQ", "No User Specified")
        #user=g.db.getUserForNick(g.currentuser, nick)
        g.db.addUserToPostable(g.currentuser, fqgn, nick)
        g.db.commit()
        return jsonify({'status':'OK', 'info': {'user':nick, 'group':fqgn}})
    else:
        useras=g.currentuser
        users=g.db.membersOfPostableFromFqin(g.currentuser,useras,fqgn)
        userdict={'users':users}
        return jsonify(userdict)

# @adsgut.route('/group/<username>/group:<groupname>/users')
# def group_users(username, groupname):
#     fqgn = username+'/group:'+groupname
#     users=g.db.usersInGroup(g.currentuser,fqgn)
#     return jsonify({'users':users})

@adsgut.route('/app', methods=['POST'])#name/description
def createApp():
    user=g.currentuser
    appspec={}
    if request.method == 'POST':
        appname=request.form.get('name')
        if not appname:
            doabort("BAD_REQ", "No App Specified")
        description=request.form.get('description', '')
        appspec['creator']=user
        appspec['name']=appname
        appspec['description']=description
        newapp=g.db.addApp(g.currentuser, user, appspec)
        return newapp.to_json()
    else:
        doabort("BAD_REQ", "GET not supported")

@adsgut.route('/app/<appowner>/app:<appname>/doinvitation', methods=['POST'])#user/op
def doInviteToApp(appowner, appname):
    #add permit to match user with appowner. BUG: what is already invited person invited (or declined person invited
    #need to add code to deal with this and understand the app invite model)
    fqan=appowner+"/app:"+appname
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
            g.db.inviteUserToApp(g.currentuser, fqan, usertobeadded)
            return jsonify({'status':'OK', 'info': {'invited':nick, 'to':fqan}})
        elif op=='accept':
            g.db.acceptInviteToApp(g.currentuser, fqan, userinvited)
            return jsonify({'status':'OK', 'info': {'invited':nick, 'to': fqan, 'accepted':True}})
        elif op=='decline':
            #BUG add something to invitations to mark declines.
            return jsonify({'status': 'OK', 'info': {'invited':nick, 'to': fqan, 'accepted':False}})
        else:
            doabort("BAD_REQ", "No Op Specified")
    else:
        doabort("BAD_REQ", "GET not supported")

#Whats the use case for this? bulk app adds which dont go through invites.
#BUG: user leakage, also, should the pythonic api part be split up into two separates?
@adsgut.route('/app/<appowner>/app:<appname>/members', methods=['GET', 'POST'])#user
def addMemberToApp_or_appMembers(appowner, appname):
    #add permit to match user with groupowner
    fqan=appowner+"/app:"+appname
    if request.method == 'POST':
        nick=request.form.get('userthere', None)
        if not nick:
            doabort("BAD_REQ", "No User Specified")
        #user=g.db.getUserForNick(g.currentuser, nick)
        g.db.addUserToPostable(g.currentuser, fqan, nick)
        g.db.commit()
        return jsonify({'status':'OK', 'info': {'user':nick, 'app':fqan}})
    else:
        useras=g.currentuser
        users=g.db.membersOfPostableFromFqin(g.currentuser,useras,fqan)
        userdict={'users':users}
        return jsonify(userdict)


@adsgut.route('/library/<libraryowner>/library:<libraryname>/members', methods=['GET', 'POST'])#user
def addMemberToLibrary_or_libraryMembers(libraryowner, libraryname):
    #add permit to match user with groupowner
    fqln=libraryowner+"/library:"+libraryname
    if request.method == 'POST':
        nick=request.form.get('userthere', None)
        if not nick:
            doabort("BAD_REQ", "No User Specified")
        #user=g.db.getUserForNick(g.currentuser, nick)
        g.db.addUserToPostable(g.currentuser, fqln, nick)
        g.db.commit()
        return jsonify({'status':'OK', 'info': {'user':nick, 'library':fqln}})
    else:
        useras=g.currentuser
        users=g.db.membersOfPostableFromFqin(g.currentuser,useras,fqln)
        userdict={'users':users}
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

@adsgut.route('/group/<groupowner>/group:<groupname>/items')
def groupItems(groupowner, groupname):
    group=postable(groupowner, groupname, "group")
    num, vals=g.dbp.getItemsForPostableQuery(g.currentuser, g.currentuser,
       [group.basic.fqin] )
    groupdict={'count':num, 'items':[simplejson.loads(v.to_json()) for v in vals]}
    return jsonify(groupdict)
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

@adsgut.route('/app/<appowner>/app:<appname>/items')
def appItems(appowner, appname):
    app=postable(appowner, appname, "app")
    num, vals=g.dbp.getItemsForPostableQuery(g.currentuser, g.currentuser,
       [app.basic.fqin] )
    appdict={'count':num, 'items':[simplejson.loads(v.to_json()) for v in vals]}
    return jsonify(appdict)
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

@adsgut.route('/library/<libraryowner>/library:<libraryname>/items')
def libraryItems(libraryowner, libraryname):
    library=postable(libraryowner, libraryname, "library")
    num, vals=g.dbp.getItemsForPostableQuery(g.currentuser, g.currentuser,
       [library.basic.fqin] )
    libdict={'count':num, 'items':[simplejson.loads(v.to_json()) for v in vals]}
    return jsonify(libdict)

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

#The users libraries
@adsgut.route('/user/<nick>/libsuserowns')
def libsUserOwns(nick):
    context=_getContext(request.args)
    useras=g.db.getUserInfo(g.currentuser, nick)
    libs=g.dbp.getTagsByOwner(g.currentuser, useras, ("eq","ads/library"), context)
    libdict={'libraries':libs}
    return jsonify(libdict)

#these are the ones user owns as well as can write to by dint of giving it to a group.
@adsgut.route('/user/<nick>/libsusercanwriteto')
def libsUserCanWriteTo(nick):
    context=_getContext(request.args)
    useras=g.db.getUserInfo(g.currentuser, nick)
    libs=g.dbp.getTagsAsMemberAndOwner(g.currentuser, useras, ("eq","ads/library"), context)
    libdict={'libraries':libs}
    return jsonify(libdict)

@adsgut.route('/user/<nick>/libsasmember')
def libsUserAsMember(nick):
    context=_getContext(request.args)
    useras=g.db.getUserInfo(g.currentuser, nick)
    libs=g.dbp.getTagsAsMemberOnly(g.currentuser, useras, ("eq","ads/library"), context)
    libdict={'libraries':libs}
    return jsonify(libdict)


#these might be supersed by tagging based results to populate the left side

#The users simple tags, not singletonmode (ie no notes), not libraries
@adsgut.route('/user/<nick>/stagsuserowns')
def sTagsUserOwns(nick):
    context=_getContext(request.args)
    useras=g.db.getUserInfo(g.currentuser, nick)
    stags=g.dbp.getTagsByOwner(g.currentuser, useras, ("ne","ads/library"), context)
    stagdict={'simpletags':stags}
    return jsonify(stagdict)

#these are the simple tags user owns as well as can write to by dint of giving it to a group.
@adsgut.route('/user/<nick>/stagsusercanwriteto')
def sTagsUserCanWriteTo(nick):
    context=_getContext(request.args)
    useras=g.db.getUserInfo(g.currentuser, nick)
    stags=g.dbp.getTagsAsMemberAndOwner(g.currentuser, useras, ("ne","ads/library"), context)
    stagdict={'simpletags':stags}
    return jsonify(stagdict)

@adsgut.route('/user/<nick>/stagsasmember')
def sTagsUserAsMember(nick):
    context=_getContext(request.args)
    useras=g.db.getUserInfo(g.currentuser, nick)
    stags=g.dbp.getTagsAsMemberOnly(g.currentuser, useras, ("ne","ads/library"), context)
    stagdict={'simpletags':stags}
    return jsonify(stagdict)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)