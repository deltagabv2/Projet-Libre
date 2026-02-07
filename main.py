from flask import Flask, render_template, redirect
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Connection à la BDD

mongo = os.getenv("MONGO_URI")
client = MongoClient(mongo)

db = client.get_database("SmartDev")



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/projet")
def projet():
    projet_data = list(db["projet"].find({}))
    return render_template("front/projet.html", projet = projet_data)

app.run(host="0.0.0.0", port=32768)