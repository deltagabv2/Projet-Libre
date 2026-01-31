from flask import Flask, render_template, redirect
import pymongo
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Connection à la BDD



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/projet")
def projet():
    return render_template("front/projet.html")

app.run(host="0.0.0.0", port=32768)