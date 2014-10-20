from flask import *
import os
import json
import pymongo
import urllib

#initial
app = Flask(__name__)
app.secret_key = os.urandom(24)

# db connect
conn = pymongo.Connection()
db = conn.votr

@app.route('/', methods=["GET"])
def index():
	items = db.item.find().sort([("post-time",-1)])
	return render_template("index.html", items=items)

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
