from flask import Flask,render_template
app = Flask(__name__)

@app.route('/')

def home():
    return render_template('index.html')

@app.route('/profile/about')

def about():
    return '<h1>This is About Page'

@app.route('/profile/<username>')

def sujeesh(username):
    return '<h1>This is %s ' %username

@app.route('/profile/<int:ID>')

def sujeesh(ID) :
    return '<h1>This is %s' %ID

app.run()