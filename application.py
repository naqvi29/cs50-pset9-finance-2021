import os

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
    return apology("show_portfolio_of_stocks", "TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        result = lookup(symbol)
        shares = request.form.get("shares")

        currentUID = session["user_id"]
        
        # if symbol is blank or does not exist, return apology
        if len(symbol) > 0 and result == None:
            return apology("Invalid Symbol", 400)
        elif len(symbol) == 0 and result == None:
            return apology("Missing Symbol", 400)

        # Render an apology if shares input is not a positive integer.
        if len(shares) == 0:
            return apology("MISSING SHARES", 400)
        elif int(shares) < 0:
            return apology("NEGATIVE NUMBER", 400)

        # access user table to get cash of current user
        # https://stackoverflow.com/questions/46723767/how-to-get-current-user-when-implementing-python-flask-security
        cash = db.execute("SELECT cash FROM users WHERE id = ?;", currentUID)
        cash = cash[0]["cash"]
        # cash is int

        price = result.get("price")
        total_buy = float(shares) * price
        # total_buy = usd(total_buy)
        total_buy = round(total_buy, 2)

        # Render an apology, without completing a purchase, if the user cannot afford the number of shares at the current price
        if total_buy > cash:
            return apology("CAN'T AFFORD", 400)
        else:
            # todo
            balance = round(float(cash) - total_buy, 2)


            # debug
            print("==========================================================================")
            print("USER INPUT")
            print("SYMBOL: " + symbol)
            print("SHARES: " + shares)
            print("==========================================================================")
            print("LOOKUP RETURN")
            print(result)
            print("==========================================================================")
            print("DATABASE OUTPUT")
            print("ID: "+ str(currentUID))
            print("CURRENT CASH: " + str(cash))
            print("CURRENT CASH DATATYPE: " + str(type(cash)))
            print("==========================================================================")
            print("BUY LOGICS")
            print("SHARES: " + str(shares))
            print("PRICE: " + str(price))
            print("TOTAL BUY: " + str(total_buy))
            print("TOTAL BUY DATATYPE: " + str(type(total_buy)))
            print("BALANCE: " + str(balance))
            print("==========================================================================")

            # When a purchase is complete, redirect the user back to the index page.
            return redirect("/")
    else:
        return render_template("/buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("show_history_transactions","TODO")


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
        result = lookup(symbol)
        # name = result.get("name")
        # price = result.get("price")
        # symbol = result.get("symbol")
        # print("==========================")
        # print(len(symbol))
        # print("==========================")
        # print(result)
        # print("==========================")
        if len(symbol) > 0 and result == None:
            return apology("Invalid Symbol", 400)
        elif len(symbol) == 0 and result == None:
            return apology("Missing Symbol", 400)
        else:
            return render_template("/quoted.html", result=result)
    else:
        return render_template("/quote.html")
        

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""   
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        hpassword = generate_password_hash(password)
        rows = db.execute("SELECT * FROM users WHERE username = ?", name)

        # if username is blank OR already exists
        if len(name) == 0 or len(rows) == 1:
            print("len(rows): " + str(len(rows)))
            print("strlen: " + str(len(name)))
            return apology("username is not available", 400)
        # if (password or confirmation is blank) or password != confirmation
        elif password != confirmation:
            return apology("passwords don't match", 400)
        else:
            db.execute("INSERT into users (username, hash) values (?, ?)", name, hpassword)
            return login()
    else:
        return render_template("/register.html")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("sell_shares_of_stock", "TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
