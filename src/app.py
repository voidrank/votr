from flask import *
import os
import json
import pymongo
import urllib

import models

#initial
app = Flask(__name__)
app.secret_key = os.urandom(24)

# db connect
conn = pymongo.Connection()
db = conn.votr

@app.route("/", methods["GET", "POST"])
def login():
	if request.method == "GET":
		return render_template("login.html", session=session)
	else:
		uid = request.form["uid"]
		passwd = request.form["passwd"]
		if models.user.login(uid=uid,passwd=passwd) == "success":
			session["uid"] = uid
			signal = "Success"
		else:
			signal = "Wrong uid or passwd"
		return render_template("login.html", session=session, signal=signal)

@app.route("/homepage/", methods=["GET"]):
def homepage():
	if models.user.exist(session["uid"]):
		hostItem = models.user.hostItem.get(session["uid"],limit=20)
		partiItem = models.user.partiItem.get(session["uid"],limit=20)
		return render_template("homepage.html", hostItem=hostItem, partiItem=partiItem)
	else:
		abort(404);


@app.route('/<hostName>/<itemName>', methods=["GET"])
def item2(hostName, itemName):
	return "1"

@app.route("/<item_name>", methods=["GET", "POST"])
def item(item_name):
	global db
	item = db.item.find_one({"name":item_name})
	if item == None:
		abort(404)
	else:
		if request.method == "GET":
			return render_template("item.html", item=item)
		elif request.method == "POST":
			form = request.form
			voter = db.voter.find_one({"uid":form["uid"]})
			if voter == None or voter['passwd'] != form['passwd']:
				return render_template("item.html", item=item, signal="Wrong Uid or Password")
			if voter["record"].get(item_name, None) != None:
				return render_template("item.html", item=item, signal="You have already voted for this item")
			if voter["record"].get(item_name, None) == None:
				voter["record"][item_name] = "user"
				item = db.item.find_one({"name":item_name})
				if item["options"][int(form["brand"])].get("count",None) == None:
					item["options"][int(form["brand"])]["count"] = 1
				else:
					item["options"][int(form["brand"])]["count"] += 1
				voter["record"][item_name] = "used"
				db.item.update({"name":item_name},item)
				db.voter.update({"uid":voter["uid"]}, voter)
				return render_template("item.html", item=item, signal="Voted successfully")
			

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8081, debug=1)
