from flask import Flask, render_template, request, session, redirect, url_for
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import bcrypt

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

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        db_users = db["user"]
        user = db_users.find_one({"username" : request.form["user"]})
        if user:
            if bcrypt.checkpw(request.form["mdp"].encode("utf-8"), user["password"]):
                session["user"] = user["user"]
                session["role"] = user["role"]
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
        if(db_users.find_one({"username" : request.form['user']})):
            return render_template('register.html', erreur = "le pseudo est déjà utilisé")
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
                    "role" : "user",
                }

                db["user"].insert_one(new_user)
                return redirect("/")
            else : 
                return render_template('front/register.html', erreur = "les mots de passe ne correspondes pas")
    else:
        return render_template('front/register.html')

app.run(host="0.0.0.0", port=32768)