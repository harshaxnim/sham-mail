from __future__ import print_function
import sys

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def hello():
	return render_template("form.html")

@app.route("/sendmail", methods = ['POST','GET'])
def sendmail():
	if request.method == 'POST':
		return 'sending mail "'+request.form['body']+'" from "'+request.form['from']+'" to "'+request.form['to']+'"...'
	elif request.method == 'GET':
		return 'you were not supposed to land here! send a mail from the home page'


if __name__ == '__main__':
	app.run(debug= True)