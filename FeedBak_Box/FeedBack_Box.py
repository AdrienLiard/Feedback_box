#!/usr/bin/env python

#-------------------------------
#Imports
#-------------------------------
import sqlite3
from flask import Flask,request,session,g,redirect,url_for,abort,render_template,flash
from contextlib import closing
#-------------------------------

#-------------------------------
#   Configuration
#-------------------------------
DATABASE='data/feedback_box.db'
DEBUG=True
PORT=8000
HOST='0.0.0.0'
SECRET_KEY = 'MySuperSecretKey'
#-------------------------------

#-------------------------------
#   Creating app
#-------------------------------
app=Flask(__name__)
app.config.from_object(__name__)
#-------------------------------

#-------------------------------
#   Database connection helpers
#-------------------------------
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def question_types():
    cursor=g.db.execute("select id,name from questiontypes").fetchall()
    for row in cursor:
        print row
    return [dict(id=row[0],name=row[1]) for row in cursor]

def questions():
    cursor=g.db.execute("select a.id,a.name,a.text,b.id as typeid,b.name as type,question_order from questions as a inner join questiontypes as b on b.id=a.type order by question_order").fetchall()
    for row in cursor:
        print row
    return [dict(id=row[0],name=row[1],text=row[2],typeid=row[3],type=row[4],question_order=row[5]) for row in cursor]


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('DatabaseSchema.sql',mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db=connect_db()

@app.teardown_request
def teardown_request(exception):
    db=getattr(g,'db',None)
    if db is not None:
        db.close()

#-------------------------------

#-------------------------------
#   App routes
#-------------------------------

@app.route('/')
def index():
    return render_template('index.html',questions=questions())


@app.route('/deletequestion/<id>')
def delete_question(id):
    order=g.db.execute("select question_order from questions").fetchone()[0]
    # Modify order
    g.db.execute("update questions set question_order=question_order + 1 where question_order>?",[order])
    g.db.commit()
    g.db.execute("delete from questions where id=?",[id])
    g.db.commit()
    flash("Question deleted")
    return redirect(url_for("index"))

@app.route('/addquestion', methods=["POST"])
def add_question():
    order=g.db.execute("select max(question_order) from questions").fetchone()[0]
    if order==None:
        order=0
    exists=g.db.execute("select count(id) from questions where name=?",[request.form['name']]).fetchone()[0] > 0
    if exists:
        flash("A question named " + request.form['name'] + " already exists",category="error")
        question={'name':request.form['name'],'type':request.form['type'],'text':request.form['text'] }
        return render_template('questions/create.html',question_types=question_types(),question=question)
    else:
        g.db.execute("insert into questions (question_order,name,[text],type,max_responses,authorize_nr) values (?,?,?,?,?,?)",[order+1,request.form['name'],request.form['text'],request.form['type'],1,0])
        g.db.commit()
    flash("Question added")
    return redirect(url_for("index"))

@app.route('/createquestion')
def create_question():
    return render_template('questions/create.html',question_types=question_types(),question=None)

@app.route('/editquestion/<int:id>')
def edit_question(id):
    cursor=g.db.execute("select a.id,a.name,a.text,b.id as typeid,b.name as type from questions as a inner join questiontypes as b on b.id=a.type where a.id=?",[id]).fetchone()
    question={'id':cursor[0],'name':cursor[1],'text':cursor[2],'typeid':cursor[3],'type':cursor[4]}
    return render_template('questions/edit.html',question_types=question_types(),question=question)

@app.route('/savequestion', methods=["POST"])
def save_question():
    g.db.execute("update questions set name=?,[text]=?,type=? where id=?",[request.form['name'],request.form['text'],request.form['type'],request.form['id']])
    g.db.commit()
    flash("Question updated")
    return redirect(url_for("index"))

@app.route('/upquestion/<id>')
def up_question(id):
    order=g.db.execute("select question_order from questions where id=?",[id]).fetchone()[0]
    if order>1:
        g.db.execute("update questions set question_order=? where question_order=?",[order,order-1])
        g.db.commit()
        g.db.execute("update questions set question_order=? where id=?",[order-1,id])
        g.db.commit()
    return redirect(url_for("index"))

@app.route('/downquestion/<id>')
def down_question(id):
    order=g.db.execute("select question_order from questions where id=?",[id]).fetchone()[0]
    max_order=g.db.execute("select max(question_order) from questions").fetchone()[0]
    if order<max_order:
        g.db.execute("update questions set question_order=? where question_order=?",[order,order+1])
        g.db.commit()
        g.db.execute("update questions set question_order=? where id=?",[order+1,id])
        g.db.commit()
    return redirect(url_for("index"))

#-------------------------------
#   App
#-------------------------------
if __name__=='__main__':
    app.run(host=app.config["HOST"],port=app.config["PORT"])
#-------------------------------