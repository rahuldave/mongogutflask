from __future__ import with_statement

import os
import sys
import datetime
import flask

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

from mongogut import whos

adsgut=app

from flask import request, session, g, redirect, url_for, \
     abort, render_template, flash, escape, make_response, jsonify, Blueprint

#x
@adsgut.before_request
def before_request():
    w=whos.Whosdb(db)
    g.db=w
    #currently set to sysuser. Atherwise have user login and set.
    g.currentuser=w.getUserForNick(None, 'adsgut')

#x
@adsgut.route('/all')
def index():
    groups=g.db.allGroups(g.currentuser)
    apps=g.db.allApps(g.currentuser)
    users=g.db.allUsers(g.currentuser)
    return flask.render_template('index.html', groups=groups, apps=apps, users=users)

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
    useras=g.db.getUserInfo(g.currentuser, nick)
    return render_template('userprofile.html', theuser=useras)

#x
@adsgut.route('/user/<nick>/groupsuserisin')
def groupsUserIsIn(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    groups=g.db.groupsForUser(g.currentuser, useras)
    groupdict={'groups':groups}
    return jsonify(groupdict)

#x
@adsgut.route('/user/<nick>/groupsuserowns')
def groupsUserOwns(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    groups=g.db.ownerOfGroups(g.currentuser, useras)
    groupdict={'groups':groups}
    return jsonify(groupdict)

#x
@adsgut.route('/user/<nick>/groupsuserisinvitedto')
def groupsUserIsInvitedTo(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    groups=g.db.groupInvitationsForUser(g.currentuser, useras)
    groupdict={'groups':groups}
    return jsonify(groupdict)

#x
@adsgut.route('/user/<nick>/appsuserisin')
def appsUserIsIn(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    apps=g.db.appsForUser(g.currentuser, useras)
    appdict={'apps':apps}
    return jsonify(appdict)

#x
@adsgut.route('/user/<nick>/appsuserowns')
def appsUserOwns(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    apps=g.db.ownerOfApps(g.currentuser, useras)
    appdict={'apps':apps}
    return jsonify(appdict)

#use this for the email invitation?
#x
@adsgut.route('/user/<nick>/appsuserisinvitedto')
def appsUserIsInvitedTo(nick):
    useras=g.db.getUserInfo(g.currentuser, nick)
    apps=g.db.appInvitationsForUser(g.currentuser, useras)
    appdict={'apps':apps}
    return jsonify(appdict)

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
@adsgut.route('/group/<groupowner>/group:<groupname>/users', methods=['GET', 'POST'])#user
def addUsertoGroup_or_groupUsers(groupowner, groupname):
    #add permit to match user with groupowner
    fqgn=groupowner+"/group:"+groupname
    if request.method == 'POST':
        nick=request.form.get('userthere', None)
        if not nick:
            doabort("BAD_REQ", "No User Specified")
        user=g.db.getUserForNick(g.currentuser, nick)
        g.db.addUserToGroup(g.currentuser, fqgn, user, None)
        g.db.commit()
        return jsonify({'status':'OK', 'info': {'user':nick, 'group':fqgn}})
    else:
        users=g.db.usersInGroup(g.currentuser,fqgn)
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
@adsgut.route('/app/<appowner>/app:<appname>/users', methods=['GET', 'POST'])#user
def addUserToApp_or_appUsers(appowner, appname):
    #add permit to match user with groupowner
    fqan=appowner+"/app:"+appname
    if request.method == 'POST':
        nick=request.form.get('userthere', None)
        if not nick:
            doabort("BAD_REQ", "No User Specified")
        user=g.db.getUserForNick(g.currentuser, nick)
        g.db.addUserToApp(g.currentuser, fqan, user, None)
        g.db.commit()
        return jsonify({'status':'OK', 'info': {'user':nick, 'app':fqan}})
    else:
        users=g.db.usersInApp(g.currentuser,fqan)
        userdict={'users':users}
        return jsonify(userdict)



#POST/GET in a lightbox?
@adsgut.route('/group/html')
def creategrouphtml():
    pass

#get group info
#x
@adsgut.route('/group/<groupowner>/group:<groupname>')
def groupInfo(groupowner, groupname):
    fqgn = groupowner+'/group:'+groupname
    group=g.db.getGroupInfo(g.currentuser, fqgn)
    return group.to_json()

#x
@adsgut.route('/group/<groupowner>/group:<groupname>/profile/html')
def groupProfileHtml(groupowner, groupname):
    fqgn = groupowner+'/group:'+groupname
    groupinfo=g.db.getGroupInfo(g.currentuser, fqgn)
    return render_template('groupprofile.html', thegroup=groupinfo)

# @adsgut.route('/group/<username>/group:<groupname>/users')
# def group_users(username, groupname):
#     fqgn = username+'/group:'+groupname
#     users=g.db.usersInGroup(g.currentuser,fqgn)
#     return jsonify({'users':users})


#TODO: do one for a groups apps

#######################################################################################################################
#######################################################################################################################

#POST/GET in a lightbox?
@adsgut.route('/app/html')
def createapphtml():
    pass

#x
@adsgut.route('/app/<appowner>/app:<appname>')
def appInfo(appowner, appname):
    fqan = appowner+'/app:'+appname
    app=g.db.getAppInfo(g.currentuser, fqan)
    return app.to_json()

#x
@adsgut.route('/app/<appowner>/app:<appname>/profile/html')
def appProfileHtml(appowner, appname):
    fqan = appowner+'/app:'+appname
    appinfo=g.db.getAppInfo(g.currentuser, fqan)
    return render_template('appprofile.html', theapp=appinfo)





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)