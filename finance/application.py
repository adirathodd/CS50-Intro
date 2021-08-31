import os


from datetime import date, datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    user_id = session.get("user_id")
    info = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    cash = info[0]['cash']
    stock_info = db.execute("SELECT symbol, SUM(shares) as shares, buy_sell FROM transactions WHERE user_id = ? GROUP BY symbol HAVING (SUM(shares)) > 0;", user_id)

    stocks_value = round(0, 2)
    for symbol in stock_info:
        quote = lookup(symbol['symbol'])
        symbol['price'] = quote['price']
        symbol['total_value'] = round(symbol['shares'] * symbol['price'], 2)
        stocks_value += round(symbol['shares'] * symbol['price'], 2)
        symbol['price'] = usd(symbol['price'])
        symbol['total_value'] = usd(symbol['total_value'])



    total_value = usd(round(stocks_value + info[0]['cash'], 2))
    stocks_value = usd(stocks_value)
    cash = usd(info[0]['cash'])



    return render_template("index.html", stock_info=stock_info, total_value=total_value, cash=cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == ("POST"):
        symbol = request.form.get("symbol").upper()
        if not symbol:
            return apology("Please enter a stock to buy", 400)
        shares = float(request.form.get("shares"))
        try:
            int(shares)
        except ValueError:
            return apology("Enter valid amount of shares", 400)

        shares = int(shares)
        if shares < 1:
            return apology("Enter valid amount of shares", 400)
        if not shares or shares < 1:
            return apology("Please enter the amount of shares to buy", 400)
        quote = lookup(symbol)
        if quote == None:
            return apology("Please enter a valid stock", 400)

        user_id = session.get("user_id")
        user = db.execute("SELECT username FROM users WHERE id = ?", user_id)
        username = user[0]['username']
        price = float(quote['price'])
        current_balance = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        cash = round(float(current_balance[0]['cash']), 2)
        total_price = round(price * shares, 2)
        new_balance = round(cash - (price * shares), 2)
        now = datetime.now()
        today = now.strftime("%d/%m/%Y %H:%M:%S")
        buy = "Buy"

        if total_price > cash:
            return apology("You do not have enough funds")

        db.execute("INSERT INTO transactions (user_id, username, symbol, price, time, shares, buy_sell) VALUES(?, ?, ?, ?, ?, ?, ?)", user_id, username, symbol, price, today, int(shares), buy)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_balance, user_id)
        return redirect("/")



    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    info = db.execute("SELECT * FROM transactions ORDER BY time DESC;")
    for row in info:
        row['price'] = usd(row['price'])
    return render_template("history.html", info = info)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Please enter a symbol")
        quote = lookup(symbol)
        if quote == None:
            return apology("Please enter a valid stock symbol")
        quote['price'] = usd(quote['price'])


        return render_template("quoted.html", quote=quote)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password1 = request.form.get("password")
        password2 = request.form.get("confirmation")

        users = db.execute("SELECT username FROM users;")
        user = []
        for row in users:
            name = row['username']
            user.append(name)

        if username in user:
            return apology("Username already im use")
        if not username:
            return apology("Please enter a username")
        if not password1 or not password2:
            return apology("Please enter a password")
        if password1 != password2:
            return apology("Please confirm your password")

        password_hash = generate_password_hash(password1)
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, password_hash)
        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == ("POST"):
        symbol = request.form.get("symbol").upper()
        if not symbol:
            return apology("Please enter a stock to sell")
        shares = float(request.form.get("shares"))
        if isinstance(shares, int) == False:
            return apology("Please enter a valid amount of shares")
        if not shares:
            return apology("Please enter the amount of shares to sell")
        quote = lookup(symbol)
        if quote == None:
            return apology("Please enter a valid stock")

        user_id = session.get("user_id")
        user = db.execute("SELECT username FROM users WHERE id = ?", user_id)
        username = user[0]['username']
        price = float(quote['price'])
        current_balance = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        cash = round(float(current_balance[0]['cash']), 2)
        total_price = round(price * shares, 2)
        new_balance = round(cash + (price * shares), 2)
        now = datetime.now()
        today = now.strftime("%d/%m/%Y %H:%M:%S")
        sell = "Sell"

        shares1 = db.execute("SELECT SUM(shares) FROM transactions WHERE user_id = ? AND symbol = ?", user_id, symbol)
        shares2 = shares1[0]['SUM(shares)']
        if shares > shares2:
            return apology("You do not have enough shares to sell")


        shares = -shares
        db.execute("INSERT INTO transactions (user_id, username, symbol, price, time, shares, buy_sell) VALUES(?, ?, ?, ?, ?, ?, ?)", user_id, username, symbol, price, today, int(shares), sell)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_balance, user_id,)

        return redirect("/")


    else:
        user_id = session.get("user_id")
        stocks_info = db.execute("SELECT symbol, SUM(shares) as shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING (SUM(shares)) > 0;", user_id)
        stocks = []
        for row in stocks_info:
            stocks.append(row['symbol'])
        return render_template("sell.html", stocks = stocks )



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
