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
PORT=8080
HOST='0.0.0.0'
SECRET_KEY = 'MySuperSecretKey'
ROOT_URL="http://bva-cxzob.fr/"
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
    'isMandatory':False,
    'libelle':u'Bonjour et bienvenue sur le réseau BVA_CX. Ce réseau vous permet de donner votre avis sur l\'Hôtel The Peninsula en répondant à un court questionnaire anonyme (moins de 2 minutes).',
    'responses':[{'value':1,'lib':u'Je participe'}]
    },
    {
    'id':1,
    'type':'single',
     'isMandatory':False,
    'libelle':u'Depuis votre arrivée, êtes vous satisfait du Peninsula ?',
    'responses':[{'value':1,'lib':u'Non'},{'value':2,'lib':u'Plutôt'},{'value':3,'lib':u'Tout à fait'},{'value':4,'lib':u'Extrêmement'}]
    },
    {
    'id':2,
    'type':'single',
     'isMandatory':False,
    'libelle':u'Quel élément vous a le plus satisfait ?',
    'responses':[{'value':1,'lib':u'La facilité d’accès'},{'value':2,'lib':u'Le cadre'},{'value':3,'lib':u'L\'accueil'},{'value':4,'lib':u'Le buffet du petit-déjeuner'}]
    },
    {
    'id':3,
    'type':'single',
     'isMandatory':False,
    'libelle':u'Quel élément vous a le moins satisfait ?',
    'responses':[{'value':1,'lib':u'La facilité d’accès'},{'value':2,'lib':u'Le cadre'},{'value':3,'lib':u'L\'accueil'},{'value':4,'lib':u'Le buffet du petit-déjeuner'}]
    }, 
    {
    'id':4,
    'type':'single',
     'isMandatory':False,
    'libelle':u'Quelle conséquence aura cet élément ?',
    'responses':[{'value':1,'lib':u'Je ne reviendrai plus'},{'value':2,'lib':u'Je vais faire une réclamation'},{'value':3,'lib':u'Je '},{'value':4,'lib':u'Aucune'}]
    },
    {
    'id':5,
    'type':'open',
     'isMandatory':False,
    'libelle':u'Avez-vous des suggestions à nous faire ?'
    },
    {
    'id':6,
    'type':'open',
     'isMandatory':False,
    'libelle':u'Laissez-nous votre adresse mail si vous souhaitez recevoir notre newsletter !'
    }]
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
        # if(request.headers.get('User-Agent').startswith('CaptiveNetworkSupport')):
        #      return "<HTML><HEAD><TITLE>Success</TITLE></HEAD><BODY>Success</BODY></HTML>"
        # if("google" in request.base_url):
        #      return "",204
        # if("android" in request.base_url):
        #      return "",204
        if(request.url_root!=ROOT_URL):
            print(request.url_root)
            return redirect(ROOT_URL)
        # id=request.cookies.get('id')
        # if(id!=None):
        #     control=g.db.execute("select count(*) as ct from interviews where guid=?",[id]).fetchone()[0]
        #     if(control==0):
        #         id=None
        resp=make_response(render_template('questionnaire.html'))
        #resp.set_cookie("id",guid)#
        return resp

@application.route("/api/nextquestion",methods=['POST'])
def nextQuestion():
    #get last question
    question=request.get_json() 
    guid=""
    if(question==None):
        question=questionnaire['questions'][0]
        guid=str(uuid.uuid4())
        g.db.execute("insert into interviews (guid) values (?)",[guid])
        g.db.commit()
        question["guid"]=guid
        question["value"]=[]
        return jsonify(question)
    else:
        print(question["id"])
        print(question["guid"])
        guid=question["guid"]
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
    if(question["id"]+1==len(questionnaire['questions'])):
        print("derniere question")
        g.db.execute("update interviews set completed=1 where guid=?",[guid])
        g.db.commit()
        return jsonify({"guid":guid,"id":-1})
    question=questionnaire['questions'][question["id"]+1]
    question["guid"]=guid
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
    #print("**********      404            ***************")
    #print(request.headers.get('User-Agent'))
    #print(request.url)
    #print("**********************************************")
    #if("google" in request.base_url):
     #       print("returning 204")
      #      return "",204
    #if("android" in request.base_url):
     #       print("returning 204")
      #      return "",204
    return redirect(ROOT_URL)

#   App
#-------------------------------

application.wsgi_app = ProxyFix(application.wsgi_app)
if __name__=='__main__':
    #application.run(host='0.0.0.0')
    #application.run(host=application.config["HOST"])
    application.run(host=application.config["HOST"],port=application.config["PORT"])
#-------------------------------
