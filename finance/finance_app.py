import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]

    TRANSACTIONS = db.execute("SELECT symbol, SUM(shares) AS shares, price, SUM(shares*price) AS total_price FROM stocks WHERE user_id = ? GROUP BY symbol", user_id)
    CASH = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    CASH = CASH[0]["cash"]

    total_sum = CASH
    for row in TRANSACTIONS:
        LOOKUP = lookup(row["symbol"])
        row["price"] = LOOKUP["price"]
        total_sum += row["total_price"]
        row["price"] = usd(row["price"])
        row["total_price"] = usd(row["total_price"])
    total_sum = usd(total_sum)
    CASH = usd(CASH)
    return render_template("index.html", transactions = TRANSACTIONS, cash = CASH, total_sum =total_sum)


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    if request.method == "GET":
        return render_template("password.html")
    else:
        NEWPASSWORD = request.form.get("newpassword")
        verification = request.form.get("passverify")
        OLDPASSWORD = request.form.get("oldpassword")

        if not NEWPASSWORD:
            return apology("Current password field is empty", 400)

        if not verification or not OLDPASSWORD:
            return apology("New password field is empty", 400)

        if verification != NEWPASSWORD:
            return apology("Passwords do not match", 400)

        NEWPASSWORD = generate_password_hash(NEWPASSWORD)

        user_id = session["user_id"]
        users = db.execute("SELECT * FROM users WHERE id = ?", user_id)

        OLDPASSWORD_db = users[0]["hash"]
        if not check_password_hash(OLDPASSWORD_db, OLDPASSWORD):
            return apology("Wrong current password", 400)

        db.execute("UPDATE users SET hash = ? WHERE id = ?", NEWPASSWORD, user_id)

        return redirect("/logout")






@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:
        SHARES = request.form.get("shares")
        SYMBOL = request.form.get("symbol").upper()
        quote = lookup(SYMBOL.upper( ))

        if not SYMBOL or quote == None:
            return apology("Missing/Invalid Symbol", 400)

        if not SHARES:
            return apology("Missing shares", 400)

        if not SHARES.isdigit():
            return apology("Introduce an INTEGER number!", 400)

        SHARES = int(SHARES)
        total_price = quote["price"] * SHARES

        balance = 0
        balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        balance = balance[0]["cash"]
        if total_price > balance:
            return apology("Cannot afford the purchase", 400)

        updated_balance = balance - total_price
        date = datetime.now()
        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_balance, session["user_id"])
        db.execute("INSERT INTO stocks(user_id, symbol, shares, price, date) VALUES (?, ?, ?, ?, ?)", session["user_id"], SYMBOL, SHARES, quote["price"], date)

        flash("Bought!")
        return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id =session["user_id"]
    TRANSACTIONS = db.execute("SELECT symbol, shares, price, date FROM stocks WHERE user_id = ?", user_id)

    return render_template("history.html", transactions = TRANSACTIONS)


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
    if request.method == "GET":
        return render_template("quote.html")
    else:
        SYMBOL = request.form.get("symbol")
        if not SYMBOL:
            return apology("Missing Symbol", 400)
        STOCK = lookup(SYMBOL.upper())
        if STOCK == None:
            return apology("Invalid Symbol", 400)
        STOCK["price"] = usd(STOCK["price"])
        return render_template("quoted.html", STOCK = STOCK)



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("missing username", 400)
        elif not request.form.get("password"):
            return apology("missing password", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match", 400)

        USERNAME = request.form.get("username")
        HASHED_PASSWORD =generate_password_hash(request.form.get("password"))
        check = db.execute("SELECT * FROM users where username = ?", USERNAME)
        if len(check) != 0:
            return apology("username is already taken", 400)

        db.execute("INSERT INTO users (username, hash) VALUES (?,?)", USERNAME, HASHED_PASSWORD)
        flash("Registered!")

        users_db = db.execute("SELECT * FROM users WHERE username = ?", USERNAME)
        session["user_id"] = users_db[0]["id"]
        return redirect("/")
    else:
        return render_template("register.html")





@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        user_id = session["user_id"]
        SYMBOLS = db.execute("SELECT symbol, SUM(shares) AS total_shares FROM stocks where user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", user_id )
        return render_template("sell.html", array = SYMBOLS)
    else:
        SHARES = request.form.get("shares")
        SYMBOL = request.form.get("symbol")

        user_id = session["user_id"]
        oldcash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        stocks_db = db.execute("SELECT symbol, SUM(shares) AS shares, price, SUM(shares*price) AS total_price FROM stocks WHERE user_id = ? AND symbol = ? GROUP BY symbol", user_id, SYMBOL)

        if not SHARES:
            return apology("Missing shares", 400)

        if not SYMBOL:
            return apology("Missing symbol", 400)

        quoted_symbol = lookup(SYMBOL)
        oldtotal_shares = stocks_db[0]["shares"]

        if oldtotal_shares < int(SHARES):
            return apology("You don't own enough shares", 400)

        if stocks_db[0]["symbol"] != SYMBOL:
            return apology("Symbol not found", 400)

        sold = int(SHARES) * quoted_symbol["price"]
        newtotal_shares = oldtotal_shares - int(SHARES)
        money = newtotal_shares * quoted_symbol["price"]
        oldtotal_price = oldtotal_shares * quoted_symbol["price"]
        newtotal_price = oldtotal_price - money
        oldcash = oldcash[0]["cash"]
        newcash = oldcash + sold
        db.execute("UPDATE users SET cash = ? WHERE id = ?" , newcash, user_id)

        date = datetime.now()
        db.execute("INSERT INTO stocks(user_id, symbol,shares,price,date) VALUES (?,?,?,?,?)",user_id, SYMBOL,(-1) * int(SHARES),quoted_symbol["price"], date)

        shares_db = db.execute("SELECT symbol, SUM(shares) AS total_shares FROM stocks WHERE user_id = ? AND symbol = ? GROUP BY symbol", user_id, SYMBOL)

        if shares_db[0]["total_shares"] == 0:
            db.execute("DELETE FROM stocks WHERE symbol = ?", SYMBOL)
        flash("Sold!")
        return redirect("/")







