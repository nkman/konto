from konto import app
from flask import Flask, jsonify, request, render_template

from konto import app
from flask import Flask, jsonify, request, render_template

@app.route('/')
def home():
	return "Hello"