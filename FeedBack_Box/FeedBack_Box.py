#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------
#Imports
#-------------------------------
from __future__ import print_function
import sqlite3
from flask import Flask,request,session,g,jsonify,redirect,url_for,abort,render_template,flash,make_response
from contextlib import closing
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
ROOT_URL="http://feedbackbox.io/"
#-------------------------------

#-------------------------------
#   Creating app
#-------------------------------
app=Flask(__name__)
app.config.from_object(__name__)
#-------------------------------

questionnaire={
    'questions':[{
    'id':0,
    'type':'multiple',
    'libelle':u'Avez vous eu des difficultés à accéder à la FeedBack Box?',
    'responses':[{'value':1,'lib':'Oui'},{'value':2,'lib':'Non'}]
    },
    {
    'id':1,
    'type':'single',
    'libelle':u'Recommandiez la FeedBack Box?',
    'responses':[{'value':1,'lib':u'Tout à fait'},{'value':2,'lib':u'Plutôt'},{'value':3,'lib':u'Plutôt pas'},{'value':4,'lib':u'Certainement pas'}]
    },
    {
    'id':2,
    'type':'open',
    'libelle':u'Un commentaire sur la FeedBack Box?'}]
}

#-------------------------------
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('DatabaseSchema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
#-------------------------------
#   App routes
#-------------------------------

@app.route('/')
def index():
        print("**********      ROOT          ***************")
        print(request.headers.get('User-Agent'))
        print(request.url)
        print("**********************************************")
        if(request.headers.get('User-Agent').startswith('CaptiveNetworkSupport')):
            return "<HTML><HEAD><TITLE>Success</TITLE></HEAD><BODY>Success</BODY></HTML>"
        if("google" in request.base_url):
            return "",204
        if(request.url_root!=ROOT_URL):
            print(request.url_root)
            return redirect(ROOT_URL)
        id=request.cookies.get('id')
        resp=make_response(render_template('questionnaire.html'))
        if(id==None):
            guid=str(uuid.uuid4())
            g.db.execute("insert into interviews (guid) values (?)",[guid])
            g.db.commit()
            resp.set_cookie("id",guid)
        return resp

@app.route("/api/nextquestion",methods=['POST'])
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

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

@app.route("/api/questionnaire")
def get_questionnaire():
    result=[]
    return jsonify(questionnaire)

@app.errorhandler(404)
def page_not_found(e):
    print("**********      404            ***************")
    print(request.headers.get('User-Agent'))
    print(request.url)
    print("**********************************************")
    return redirect(ROOT_URL)
#   App
#-------------------------------
if __name__=='__main__':
    app.run(host=app.config["HOST"],port=app.config["PORT"])
#-------------------------------