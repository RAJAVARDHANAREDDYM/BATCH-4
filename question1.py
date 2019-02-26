from flask import Flask, render_template, url_for
from flask import request, redirect, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from question import Base, Question


engin = create_engine('sqlite:///question.db',
			connect_args={'check_same_thread':False},echo=True)
Base.metadata.create_all(engin)
DBSession = sessionmaker(bind=engin)
session=DBSession()
app = Flask(__name__)

@app.route('/addQuestion',methods=['POST','GET'])
def addQuestion():
	if request.method=="POST":
		name=request.form['name']
		level=request.form['level']
		co=request.form['co']
		unit=request.form['unit']
		newquestion = Question(name=name,level=level,co=co,unit=unit)
		session.add(newquestion)
		session.commit()
		flash("your DATA INSERTED successfully")
		return render_template('question.html')
	else:
		return render_template('question.html')


if __name__ == '__main__':
	app.secret_key="secret_key"
	app.debug = True
	app.run(host='0.0.0.0',port=8000)
