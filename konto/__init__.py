import os
from flask import Flask, jsonify, request, render_template

tempdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

app = Flask("konto", template_folder=tempdir)
from konto import routes
from routes import mobileapp
