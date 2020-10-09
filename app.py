from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        if session.get("logged_in"):
            return redirect(url_for('home'))
        else:
            return render_template('index.html')
    elif request.method == "POST":
        return "POSTED!"
    else:
        return render_template("index.html")
        
    

@app.route('/register')
def register():
    return "Under development."

@app.route('/login')
def login():
    return "Under development."

@app.route('/home')
def home():
    return "Under development."
