from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta, date, datetime
import time
import hashlib
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from yahoo_fin import stock_info as si


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "jk37kg85jhlf62ii4"
salt = "k8js23hds"

badwords = ["4r5e", "5h1t", "5hit", "a55", "anal", "anus", "ar5e", "arrse", "arse", "ass", "ass-fucker", "asses", "assfucker", "assfukka", "asshole", "assholes", "asswhole", "a_s_s", "b!tch", "b00bs", "b17ch", "b1tch", "ballbag", "balls", "ballsack", "bastard", "beastial", "beastiality", "bellend", "bestial", "bestiality", "bi+ch", "biatch", "bitch", "bitcher", "bitchers", "bitches", "bitchin", "bitching", "bloody", "blow job", "blowjob", "blowjobs", "boiolas", "bollock", "bollok", "boner", "boob", "boobs", "booobs", "boooobs", "booooobs", "booooooobs", "breasts", "buceta", "bugger", "bum", "bunny fucker", "butt", "butthole", "buttmuch", "buttplug", "c0ck", "c0cksucker", "carpet muncher", "cawk", "chink", "cipa", "cl1t", "clit", "clitoris", "clits", "cnut", "cock", "cock-sucker", "cockface", "cockhead", "cockmunch", "cockmuncher", "cocks", "cocksuck", "cocksucked", "cocksucker", "cocksucking", "cocksucks", "cocksuka", "cocksukka", "cok", "cokmuncher", "coksucka", "coon", "cox", "crap", "cum", "cummer", "cumming", "cums", "cumshot", "cunilingus", "cunillingus", "cunnilingus", "cunt", "cuntlick", "cuntlicker", "cuntlicking", "cunts", "cyalis", "cyberfuc", "cyberfuck", "cyberfucked", "cyberfucker", "cyberfuckers", "cyberfucking", "d1ck", "damn", "dick", "dickhead", "dildo", "dildos", "dink", "dinks", "dirsa", "dlck", "dog-fucker", "doggin", "dogging", "donkeyribber", "doosh", "duche", "dyke", "ejaculate", "ejaculated", "ejaculates", "ejaculating", "ejaculatings", "ejaculation", "ejakulate", "f u c k", "f u c k e r", "f4nny", "fag", "fagging", "faggitt", "faggot", "faggs", "fagot", "fagots", "fags", "fanny", "fannyflaps", "fannyfucker", "fanyy", "fatass", "fcuk", "fcuker", "fcuking", "feck", "fecker", "felching", "fellate", "fellatio", "fingerfuck", "fingerfucked", "fingerfucker", "fingerfuckers", "fingerfucking", "fingerfucks", "fistfuck", "fistfucked", "fistfucker", "fistfuckers", "fistfucking", "fistfuckings", "fistfucks", "flange", "fook", "fooker", "fuck", "fucka", "fucked", "fucker", "fuckers", "fuckhead", "fuckheads", "fuckin", "fucking", "fuckings", "fuckingshitmotherfucker", "fuckme", "fucks", "fuckwhit", "fuckwit", "fudge packer", "fudgepacker", "fuk", "fuker", "fukker", "fukkin", "fuks", "fukwhit", "fukwit", "fux", "fux0r", "f_u_c_k", "gangbang", "gangbanged", "gangbangs", "gaylord", "gaysex", "goatse", "God", "god-dam", "god-damned", "goddamn", "goddamned", "hardcoresex", "hell", "heshe", "hoar", "hoare", "hoer", "homo", "hore", "horniest", "horny", "hotsex", "jack-off", "jackoff", "jap", "jerk-off", "jism", "jiz", "jizm", "jizz", "kawk", "knob", "knobead", "knobed", "knobend", "knobhead", "knobjocky", "knobjokey", "kock", "kondum", "kondums", "kum", "kummer", "kumming", "kums", "kunilingus", "l3i+ch", "l3itch", "labia", "lust", "lusting", "m0f0", "m0fo", "m45terbate", "ma5terb8", "ma5terbate", "masochist", "master-bate", "masterb8", "masterbat*", "masterbat3", "masterbate", "masterbation", "masterbations", "masturbate", "mo-fo", "mof0", "mofo", "mothafuck", "mothafucka", "mothafuckas", "mothafuckaz", "mothafucked", "mothafucker", "mothafuckers", "mothafuckin", "mothafucking", "mothafuckings", "mothafucks", "mother fucker", "motherfuck", "motherfucked", "motherfucker", "motherfuckers", "motherfuckin", "motherfucking", "motherfuckings", "motherfuckka", "motherfucks", "muff", "mutha", "muthafecker", "muthafuckker", "muther", "mutherfucker", "n1gga", "n1gger", "nazi", "nigg3r", "nigg4h", "nigga", "niggah", "niggas", "niggaz", "nigger", "niggers", "nob", "nob jokey", "nobhead", "nobjocky", "nobjokey", "numbnuts", "nutsack", "orgasim", "orgasims", "orgasm", "orgasms", "p0rn", "pawn", "pecker", "penis", "penisfucker", "phonesex", "phuck", "phuk", "phuked", "phuking", "phukked", "phukking", "phuks", "phuq", "pigfucker", "pimpis", "piss", "pissed", "pisser", "pissers", "pisses", "pissflaps", "pissin", "pissing", "pissoff", "poop", "porn", "porno", "pornography", "pornos", "prick", "pricks", "pron", "pube", "pusse", "pussi", "pussies", "pussy", "pussys", "rectum", "retard", "rimjaw", "rimming", "s hit", "s.o.b.", "sadist", "schlong", "screwing", "scroat", "scrote", "scrotum", "semen", "sex", "sh!+", "sh!t", "sh1t", "shag", "shagger", "shaggin", "shagging", "shemale", "shi+", "shit", "shitdick", "shite", "shited", "shitey", "shitfuck", "shitfull", "shithead", "shiting", "shitings", "shits", "shitted", "shitter", "shitters", "shitting", "shittings", "shitty", "skank", "slut", "sluts", "smegma", "smut", "snatch", "son-of-a-bitch", "spac", "spunk", "s_h_i_t", "t1tt1e5", "t1tties", "teets", "teez", "testical", "testicle", "tit", "titfuck", "tits", "titt", "tittie5", "tittiefucker", "titties", "tittyfuck", "tittywank", "titwank", "tosser", "turd", "tw4t", "twat", "twathead", "twatty", "twunt", "twunter", "v14gra", "v1gra", "vagina", "viagra", "vulva", "w00se", "wang", "wank", "wanker", "wanky", "whoar", "whore", "willies", "willy", "xrated", "xxx"];

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

class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    timestamp = db.Column(db.String)



#METHODS
def login(username, password):
    if request.form.get('username').isalpha():
        passwd = hashlib.md5((password+salt).encode()).hexdigest()
        user = User.query.filter_by(username=username, password=passwd).first()
        if user:
            session['logged_in'] = True
            session['username'] = user.username
            session['user_id'] = user.id
            login = UserActivity(user_id=user.id, timestamp=time.time())
            db.session.add(login)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            flash("Username and/or password incorrect.")
            return render_template('index.html')
    else:
        flash("Username can only be letters a-z & A-Z")
        return render_template('index.html')


def registerUser(username, password, email):
    if request.form.get('username').isalpha():
        if username in badwords:
            flash("Username contains a foul word.")
            return render_template('register.html')
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
                login = UserActivity(user_id=user.id, timestamp=time.time())
                db.session.add(login)
                db.session.commit()
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
        self.currentPrice = round(si.get_live_price(abbr), 2)
        self.dayHigh = self.cs.info['dayHigh']
        self.dayLow = self.cs.info['dayLow']
        self.currentAskSize = self.cs.info['askSize']
        self.currentBid = self.cs.info['bid']
        self.currentBidSize = self.cs.info['bidSize']
        self.shortName = self.cs.info['shortName']
        self.symbol = self.cs.info['symbol']
        self.volume = self.cs.info['volume']
        self.marketClose = self.cs.info['previousClose']
    
    def plotData(self):
        data = yf.download(self.symbol,'2020-01-01', date.today())
        data.Close.plot()
        fname = "./static/img/" + self.symbol + ".png"
        plt.savefig(fname, dpi=None, facecolor='w', edgecolor='w',
        orientation='landscape')

class Purchase():
    def __init__(self, stock, amount, owner_id):
        self.stock = stock
        self.amount = amount
        self.owner_id = owner_id


    def validate(self):
        if self.stock.currentPrice >= 1 and float(self.amount) >= 0.1:
            return True
        else:
            return False

    def completePurchase(self):
        user = User.query.get(session.get('user_id'))
        price = self.stock.currentPrice * float(self.amount)
        brookagePrice = 5 * price / 100
        totalPrice = price + brookagePrice
        if totalPrice <= user.wallet:
            user.wallet = user.wallet - totalPrice
            activeStock = ActiveStocks(
                owner_id=session.get('user_id'), name=self.stock.shortName, abbr=self.stock.symbol,
                buyPrice=self.stock.currentPrice,buyTime=time.time(),amount=self.amount
                )
            db.session.add(activeStock)
            db.session.commit()
            return True
        else:
            return False
     
class Sell():

    def __init__(self, ident, stocks):
        self.id = int(ident)
        self.stocks = stocks
        self.amount = self.stocks[self.id].amount
        self.dbid = self.stocks[self.id].id
        self.cs = Stock(self.stocks[self.id].abbr)

    def validate(self):
        if self.cs.currentPrice > 0:
            return True
        else:
            return False

    def complete(self):
        self.price = self.cs.currentPrice * float(self.amount)
        user = User.query.get(session.get('user_id'))
        user.wallet = user.wallet + self.price
        active_stock = ActiveStocks.query.get(self.dbid)
        db.session.delete(active_stock)
        db.session.commit()
        return True

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
        user = User.query.get(session.get('user_id'))
        return redirect(url_for('summary'))
    else:
        return redirect(url_for('index'))


@app.route('/summary', methods=['GET', 'POST'])
def summary():
    if session.get('logged_in'):
        stocks = ActiveStocks.query.filter_by(owner_id=session.get('user_id')).all()
        currentStocksObjects = []
        for i in range(len(stocks)):
            cs = si.get_live_price(stocks[i].abbr)
            currentStocksObjects.append(cs)
        user = User.query.get(session.get('user_id'))
        
        if request.method == "POST":
            req = request.form
            for r in req:
                transaction = Sell(r, stocks)
                if transaction.validate():
                    if transaction.complete():
                        return redirect(url_for('summary'))
                else:
                    return False
        return render_template('new_home.html', stocks=stocks, datetime=datetime, user=user, cs=currentStocksObjects)
    else:
        return redirect(url_for('index'))

@app.route('/lookup', methods=['GET', 'POST'])
def lookup():
    if session.get('logged_in'):
        user = User.query.get(session.get('user_id'))
        if request.method == "GET":
            return render_template('new_lookup.html', user=user)
        elif request.method == "POST":
            if request.form.get('abbr'):
                abbr = request.form.get('abbr')
                try:
                    stock = Stock(abbr)
                    session['cs'] = abbr
                except:
                    flash("Stock not found.")
                    return render_template('new_lookup.html', user=user)
                stock.plotData()
                
                return render_template('new_lookup.html', stock=stock, user=user)
            else:
                if request.form.get('amount'):
                    amount = request.form.get('amount')
                    cs = Stock(session['cs'])
                    purchase = Purchase(cs, amount, session.get('user_id'))
                    if purchase.validate():
                        if purchase.completePurchase():
                            flash("The stock has been bought!")
                        else:
                            flash("You do not have enough money for these stocks.")
                    else:
                        flash("The stock can not be bought at this time.")
                return render_template('new_lookup.html', stock=cs, user=user)
            flash("Stock not found.")
            return render_template('new_lookup.html', user=user)
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
