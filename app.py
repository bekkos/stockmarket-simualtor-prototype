from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta, date
import hashlib
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "jk37kg85jhlf62ii4"
salt = "k8js23hds"

db = SQLAlchemy(app)

#DatabaseLogic
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(255))
    email = db.Column(db.String(255))
    wallet = db.Column(db.Float)
    team_id = db.Column(db.Integer)

class ActiveStocks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer)
    name = db.Column(db.String)
    abbr = db.Column(db.String)
    buyPrice = db.Column(db.Float)
    buyTime = db.Column(db.String)
    amount = db.Column(db.Integer)




#METHODS
def login(username, password):
    if request.form.get('username').isalpha():
        passwd = hashlib.md5((password+salt).encode()).hexdigest()
        user = User.query.filter_by(username=username, password=passwd).first()
        if user:
            session['logged_in'] = True
            session['username'] = user.username
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            flash("Username and/or password incorrect.")
            return render_template('index.html')
    else:
        flash("Username can only be letters a-z & A-Z")
        return render_template('index.html')


def registerUser(username, password, email):
    if request.form.get('username').isalpha():
        passwd = hashlib.md5((password+salt).encode()).hexdigest()
        user = User.query.filter_by(username=username).first()
        if user is None:
            user = User.query.filter_by(email=email).first()
            if user is None:
                user = User(username=username, password=passwd, email=email, wallet=10000.0)
                db.session.add(user)
                db.session.commit()
                session['logged_in'] = True
                session['username'] = user.username
                session['user_id'] = user.id
                return redirect(url_for('home'))
        flash("Username or email is already taken")
        return render_template('register.html')
    else:
        flash("Username can only be letters a-z & A-Z")
        return render_template('register.html')



#Classess
class Stock():

    def __init__(self, abbr):
        self.cs = yf.Ticker(abbr)
        self.currentPrice = self.cs.info['ask']
        self.dayHigh = self.cs.info['dayHigh']
        self.dayLow = self.cs.info['dayLow']
        self.currentAskSize = self.cs.info['askSize']
        self.currentBid = self.cs.info['bid']
        self.currentBidSize = self.cs.info['bidSize']
        self.shortName = self.cs.info['shortName']
        self.symbol = self.cs.info['symbol']
        self.volume = self.cs.info['volume']
    
    def plotData(self):
        data = yf.download(self.symbol,'2020-01-01', date.today())
        data.Close.plot()
        fname = "./static/img/" + self.symbol + ".png"
        plt.savefig(fname, dpi=None, facecolor='w', edgecolor='w',
        orientation='landscape')
        

#Before Request
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        if session.get("logged_in"):
            return redirect(url_for('home'))
        else:
            return render_template('index.html')
    elif request.method == "POST":
        return login(request.form.get('username'), request.form.get('password'))
    else:
        return render_template("index.html")
        
    

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')
    elif request.method == "POST":
        return registerUser(request.form.get('username'), request.form.get('password'), request.form.get('email'))


@app.route('/home')
def home():
    if session.get('logged_in'):
        return render_template('home.html')
    else:
        return redirect(url_for('index'))


@app.route('/summary')
def summary():
    if session.get('logged_in'):
        return render_template('summary.html')
    else:
        return redirect(url_for('index'))

@app.route('/lookup', methods=['GET', 'POST'])
def lookup():
    if session.get('logged_in'):
        if request.method == "GET":
            return render_template('lookup.html')
        elif request.method == "POST":
            if request.form.get('abbr'):
                abbr = request.form.get('abbr')
                try:
                    stock = Stock(abbr)
                except:
                    flash("Stock not found.")
                    return render_template('lookup.html')
                stock.plotData()
                return render_template('lookup.html', stock=stock)
            flash("Stock not found.")
            return render_template('lookup.html')
    else:
        return redirect(url_for('index'))



@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('user_id', None)
    return render_template('logged_out.html')


#Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
