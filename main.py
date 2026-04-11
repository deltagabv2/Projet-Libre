from flask import Flask, render_template, request, session, redirect, url_for
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import bcrypt
from bson import Code, Binary
from bson.json_util import dumps
from bson.objectid import ObjectId
import random
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

load_dotenv()

app = Flask(__name__)

# Connection à la BDD

mongo = os.getenv("MONGO_URI")
client = MongoClient(mongo)

db = client.get_database("SmartDev")
app.secret_key = os.urandom(24)



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/projet")
def projet():
    projet_data = list(db["projet"].find({}))
    return render_template("front/projet.html", projet = projet_data)

@app.route("/publish")
def publish():
    return render_template("front/publish.html")

@app.route("/search", methods = ["GET"])
def search():
    query = request.args.get("q", "").strip()

    if query == "":
        results_projet = list(db["projet"].find({}))
        results_user = list(db["user"].find({}))
    else:
        results_projet = list(db["projet"].find({
            "$or" : [
                {"titreProjet" : {"$regex" : query, "$options" : "i"}},
                {"descriptionProjet" : {"$regex" : query, "$options" : "i"}},
                {"auteurProjet" : {"$regex" : query, "$options" : "i"}}
            ]
        }))
        results_user = list(db["user"].find({
            "$or" : [
                {"username" : {"$regex" : query, "$options" : "i"}}
            ]
        }))
    if len(results_projet + results_user) <= 0:
        return render_template("front/search_result.html", erreur = "Il n'y a pas de résultats pour :", query=query)
    else:
        return render_template("front/search_result.html", erreur = "Voici les résultats pour : ", projet = results_projet, user = results_user, query=query)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        db_users = db["user"]
        user = db_users.find_one({"username" : request.form["user"]})
        if user:
            if bcrypt.checkpw(request.form["mdp"].encode("utf-8"), user["password"]):
                session["role"] = user["role"]
                session["user"] = request.form["user"]
                session["image"] = user["image"]
                return redirect("/projet")
            else:
                return render_template("front/login.html", erreur = "Erreur : Mot de Passe Incorrect")
        else:
            return render_template("front/login.html", erreur = "Erreur : Nom d'Utilisateur Incorrect")    
    else:
        return render_template("front/login.html")  

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        db_users = db["user"]
        image = random.randint(1, 4)
        img_path = "../../static/imageUser/" + str(image) + ".jpg"
        if(db_users.find_one({"username" : request.form['user']})):
            return render_template('front/register.html', erreur = "le pseudo est déjà utilisé")
        else : 
            if(request.form["mdp"] == request.form['confirm_mdp']):
                utilisateur = request.form['user']
                mdp = request.form['mdp']

                #Hash du mot de passe
                mdp_crypte = mdp.encode("utf-8")
                salt = bcrypt.gensalt()
                mdp_hash = bcrypt.hashpw(mdp_crypte, salt)

                new_user = {
                    "username" : utilisateur,
                    "password" : mdp_hash,
                    "description" : "",
                    "date" : datetime.now(timezone(timedelta(hours=2))),
                    "image" : img_path,
                    "role" : "user",
                }

                db["user"].insert_one(new_user)
                session["role"] = "user"
                session["image"] = img_path
                session["user"] = utilisateur
                return redirect("/projet")
            else : 
                return render_template('front/register.html', erreur = "les mots de passe ne correspondes pas")
    else:
        return render_template('front/register.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/projet/<id_projet>")
def pageprojet(id_projet):
    projet = db["projet"].find_one({"_id":ObjectId(id_projet)})
    return render_template("front/pageprojet.html", projet = projet)

@app.route("/user/<id_user>")
def pageuser(id_user):
    user = db["user"].find_one({"_id":ObjectId(id_user)})
    
    results_projet = list(db["projet"].find({
            "$or" : [
                {"auteurProjet" : {"$regex" : user['username'], "$options" : "i"}}
            ]
        }))
    return render_template("front/pageuser.html", user = user, projet = results_projet)

@app.route("/compte/<username>")
def compteuser(username):
    if session["user"]:
        user = db["user"].find_one({"username" : username})
        return render_template("front/compte.html", user = user)
    else:
        return redirect(url_for("projet"))

#################################################
#                     ADMIN                     #
#################################################

@app.route("/admin", methods = ["GET", "POST"] )
def admin():
    projet_data = list(db["projet"].find({}))
    user_data = list(db["user"].find({}))
    if "user" in session and session["role"] == "admin":
        return render_template("admin/admin_accueil.html", user = user_data, projet = projet_data)
    else:
        return redirect(url_for("projet"))
    
@app.route("/admin/update_role/<user_id>", methods=["POST"])
def update_role(user_id):
    if "user" in session and session["role"] == "admin":
        new_role = request.form.get("role")
        
        db["user"].update_one({"_id" : ObjectId(user_id)}, {"$set" : {"role" : new_role}})
    return redirect(url_for("admin"))

@app.route("/admin/delete_user/<user_id>")
def delete_user(user_id):
    if "user" in session and session["role"] == "admin":
        db["user"].delete_one({"_id" : ObjectId(user_id)})
    return redirect(url_for("admin"))

@app.route("/admin/delete_projet/<projet_id>")
def delete_projet(projet_id):
    if "user" in session and session["role"] == "admin":
        db["projet"].delete_one({"_id" : ObjectId(projet_id)})
    return redirect(url_for("admin"))





app.run(host="0.0.0.0", port=32768)