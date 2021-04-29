from flask import Flask, render_template, redirect, url_for
import json

app = Flask(__name__)

@app.route('/')
def index():
	file = open('rumahsakit_new2.json')
	json_data = json.load(file)
	return render_template('mapsv2.html',rows=json_data)

# @app.route('/maps')
# def maps():
# 	file = open('rumahsakit_new2.json')
# 	json_data = json.load(file)
# 	return render_template("mapsv2.html",rows=json_data)

if __name__ == '__main__':
	app.run(debug=True)