#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------
#Imports
#-------------------------------
from __future__ import print_function
import sqlite3
from flask import Flask,request,session,g,jsonify,redirect,url_for,abort,render_template,flash,make_response
from contextlib import closing
from werkzeug.contrib.fixers import ProxyFix
import uuid

#-------------------------------

#-------------------------------
#   Configuration
#-------------------------------
DATABASE='data/feedback_box.db'
DEBUG=True
PORT=80
HOST='0.0.0.0'
SECRET_KEY = 'MySuperSecretKey'
ROOT_URL="http://bvabox.fr/"
#-------------------------------

#-------------------------------
#   Creating app
#-------------------------------
application=Flask(__name__)
application.config.from_object(__name__)
#-------------------------------

questionnaire={
    'questions':[{
    'id':0,
    'type':'single',
    'libelle':u'Avez-vous eu des difficultés à accéder à la BVA Box?',
    'responses':[{'value':1,'lib':'Oui'},{'value':2,'lib':'Non'}]
    },
    {
    'id':1,
    'type':'single',
    'libelle':u'Recommanderiez la BVA Box?',
    'responses':[{'value':1,'lib':u'Tout à fait'},{'value':2,'lib':u'Plutôt'},{'value':3,'lib':u'Plutôt pas'},{'value':4,'lib':u'Pas du tout'}]
    },
    {
    'id':2,
    'type':'single',
    'libelle':u'Quel nom donneriez-vous à la BVA Box?',
    'responses':[{'value':1,'lib':u'FeedBack Box'},{'value':2,'lib':u'BVA Box'},{'value':3,'lib':u'Sat Box'},{'value':4,'lib':u'BoCX BVA'}]
    },
    {
    'id':3,
    'type':'open',
    'libelle':u'Un commentaire sur la BVA Box?'}]
}

#-------------------------------
def connect_db():
    return sqlite3.connect(application.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with application.open_resource('DatabaseSchema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@application.before_request
def before_request():
    g.db = connect_db()

@application.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
#-------------------------------
#   App routes
#-------------------------------

@application.route('/')
def index():
        print("**********      ROOT          ***************")
        print(request.headers.get('User-Agent'))
        print(request.url)
        print("**********************************************")
        if(request.headers.get('User-Agent').startswith('CaptiveNetworkSupport')):
            return "<HTML><HEAD><TITLE>Success</TITLE></HEAD><BODY>Success</BODY></HTML>"
        if("google" in request.base_url):
            return "",204
        if("android" in request.base_url):
            return "",204
        # if(request.url_root!=ROOT_URL):
        #     print(request.url_root)
        #     return redirect(ROOT_URL)
        id=request.cookies.get('id')
        resp=make_response(render_template('questionnaire.html'))
        if(id==None):
            guid=str(uuid.uuid4())
            g.db.execute("insert into interviews (guid) values (?)",[guid])
            g.db.commit()
            resp.set_cookie("id",guid)
        return resp

@application.route("/api/nextquestion",methods=['POST'])
def nextQuestion():
    guid=request.cookies.get('id')
    #get last question
    question=request.get_json()
    if(question==None):
        question=questionnaire['questions'][0]
    else:
        print(question["id"])
        if(question["type"]=='open'):
            g.db.execute("insert into interviewsdata (guid,question_id,open_value) values (?,?,?)",[guid,question["id"],question["value"][0]])
            g.db.commit()
        elif(question["type"]=='single'):
            g.db.execute("insert into interviewsdata (guid,question_id,closed_value) values (?,?,?)",[guid,question["id"],question["value"][0]])
            g.db.commit()
        elif(question["type"]=="multiple"):
            for val in question["value"]:
                g.db.execute("insert into interviewsdata (guid,question_id,closed_value) values (?,?,?)",[guid,question["id"],val])
                g.db.commit()
        g.db.execute("update interviews set last_question=? where guid=?",[question["id"],guid])
        g.db.commit()
    maxQuestionAnswered=g.db.execute("select last_question from interviews where guid=?",[guid]).fetchone()[0]
    print(maxQuestionAnswered)
    if(maxQuestionAnswered+1==len(questionnaire['questions'])):
        print(len(questionnaire['questions']))
        g.db.execute("update interviews set completed=1 where guid=?",[guid])
        g.db.commit()
        return jsonify({"id":-1})
    question=questionnaire['questions'][maxQuestionAnswered+1]
    question["value"]=[]
    return jsonify(question)

@application.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

@application.route("/api/results")
def results():
    result={"data":[]}
    for question in questionnaire["questions"]:
        cursor=g.db.cursor()
        temp={'id':question['id'],'libelle':question["libelle"],'type':question["type"],'show':False,'data':[]}
        if question["type"]=="open":
            print("open")
            for response in cursor.execute("select open_value from interviewsdata where question_id=?",[question["id"]]).fetchall():
                temp["data"].append({'value':response[0]})             
        else:
            for response in question['responses']:
                val=cursor.execute("select count(*) as ct from interviewsdata where question_id=? and closed_value=?",[question["id"],response['value']]).fetchone()[0]
                temp["data"].append({'label':response['lib'],'code':response['value'],'value':val})
        result["data"].append(temp)
    return jsonify(result)

@application.route("/api/questionnaire")
def get_questionnaire():
    result=[]
    return jsonify(questionnaire)

@application.errorhandler(404)
def page_not_found(e):
    print("**********      404            ***************")
    print(request.headers.get('User-Agent'))
    print(request.url)
    print("**********************************************")
    if("google" in request.base_url):
            print("returning 204")
            return "",204
    if("android" in request.base_url):
            print("returning 204")
            return "",204
    return redirect(ROOT_URL)

#   App
#-------------------------------

application.wsgi_app = ProxyFix(application.wsgi_app)
if __name__=='__main__':
    #application.run(host='0.0.0.0')
    #application.run(host=application.config["HOST"])
    application.run(host=application.config["HOST"],port=application.config["PORT"])
#-------------------------------
