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
    print("\x1b[6;30;42m" + "-------------------------- START INDEX --------------------------" + "\x1b[0m")

    spent_cash = db.execute("SELECT spent_cash FROM profile WHERE user_id = ? ORDER BY date_time DESC LIMIT 1", session["user_id"])
    spent_cash = spent_cash[0]["spent_cash"]

    # get total shares of each symbol
    portfolios = db.execute("SELECT symbol, SUM(shares) as totalshares FROM activities WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", session["user_id"])

    print("PORTFOLIO FROM DB")
    print(portfolios)

    # user never spent any cash before - get cash from users table
    if spent_cash == 0:
        print("=================================================================")
        print("SPENT CASH")
        print("FALSE - user (" + session["username"] + ") HAVE NOT purchase stock")

        # get initial cash value from users table
        cash = db.execute("SELECT cash FROM users WHERE id = ?;", session["user_id"])
        cash_before = usd(cash[0]["cash"])
        print("CASH BALANCE")
        print(cash_before)
        print("\x1b[6;37;41m" + "--------------------------- END INDEX ---------------------------" + "\x1b[0m")

        return render_template("/index.html", portfolios=portfolios, cash_before=cash_before)

    # users have spent cash before - get money from users last recent activity
    elif spent_cash == 1:
        print("SPENT CASH")
        print("TRUE - user (" + session["username"] + ") HAVE purchase stock")

        cash = db.execute("SELECT cash_after FROM activities WHERE user_id = ? ORDER BY date_time DESC LIMIT 1;", session["user_id"])
        cash_before = usd(cash[0]["cash_after"])
        print("CASH BALANCE")
        print(cash_before)

        # INSERT dict-test.py
        totals_list = []

        # loop mechanics
        print("=================================================================")
        print("GET LOOKUP & UPDATE PORTFOLIOS DICT")
        print("=================================================================")
        for i in range(len(portfolios)):
            # update portfolio dict with info from lookup()
            portfolios[i].update(lookup(portfolios[i]["symbol"]))

            # TODO - TOTAL = totalshares * price, add to dictionary
            totals = portfolios[i]["totalshares"] * portfolios[i]["price"]
            totals_list.append(totals)
            portfolios[i].update(totals = totals)

            # usd-fy price and totals
            portfolios[i].update(price = usd(portfolios[i]["price"]))
            portfolios[i].update(totals = usd(portfolios[i]["totals"]))
        print("=================================================================")
        print("PORTFOLIOS DICT UPDATED")
        print(portfolios)
        print("=================================================================")

        portfoliototal = usd(sum(totals_list) + cash[0]["cash_after"])

        print("\x1b[6;37;41m" + "--------------------------- END INDEX ---------------------------" + "\x1b[0m")

        return render_template("/index.html", portfolios=portfolios, cash_before=cash_before, portfoliototal=portfoliototal)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        print("\x1b[6;30;42m" + "--------------------------- BUY START ---------------------------" + "\x1b[0m")

        spent_cash = db.execute("SELECT spent_cash FROM profile WHERE user_id = ? ORDER BY date_time DESC LIMIT 1", session["user_id"])
        spent_cash = spent_cash[0]["spent_cash"]
        symbol = request.form.get("symbol")
        symbol = symbol.upper()

        shares = request.form.get("shares")
        print("================================================================")
        result = lookup(symbol)
        print("================================================================")
        print("SHARES DATA TYPE from form.get")
        print(type(shares))
        print(shares)
        print("\x1b[4;30;47m" + "USER SPENT CASH?"+ "\x1b[0m")
        if spent_cash == 0:
            print("NO - get cash from user table")
        elif spent_cash == 1:
            print("YES - get cash from activities table")

        # if symbol is blank or does not exist, return apology
        if len(symbol) > 0 and result == None:
            return apology("Invalid Symbol")
        elif len(symbol) == 0 and result == None:
            return apology("Missing Symbol")

        # Render an apology if shares input is not a positive integer.
        if len(shares) == 0:
            return apology("MISSING SHARES")
        elif shares.isalpha() == True or shares.isnumeric() == False:
            return apology("INVALID SHARES")
        # elif shares.isnumeric() == True:
        else:
            shares = int(shares)

            if shares <= 0:
                return apology("MUST BE POSITIVE NUMBER")

        if spent_cash == 0:
            # access user table to get cash of current user
            # https://stackoverflow.com/questions/46723767/how-to-get-current-user-when-implementing-python-flask-security
            cash = db.execute("SELECT cash FROM users WHERE id = ?;", session["user_id"])
            # cash is int
            cash_before = cash[0]["cash"]

            # get price of share from lookup result
            price = result.get("price")

            # compute total purchase
            total_purchase = float(shares) * price
            # total_purchase = round(total_purchase, 2)

            total_purchase_usd = total_purchase

            # Render an apology, without completing a purchase, if the user cannot afford the number of shares at the current price
            if total_purchase > cash_before:
                return apology("CAN'T AFFORD")
            else:
                # Compute cash left after purchase
                cash_after = round(float(cash_before) - total_purchase, 2)
                # cash_after = round(float(cash_before) - total_purchase, 2)


                # debug
                print("=================================================================")
                print("USER INPUT")
                print("SYMBOL: " + symbol)
                print("SHARES: " + str(shares))
                print("LOOKUP RETURN")
                print(result)
                print("DATABASE OUTPUT")
                print("ID: "+ str(session["user_id"]))
                print("CURRENT CASH: " + str(cash_before))
                print("CURRENT CASH DATATYPE: " + str(type(cash_before)))
                print("BUY LOGICS")
                print("SHARES: " + str(shares))
                print("PRICE: " + str(price))
                print("TOTAL BUY: " + str(total_purchase))
                print("TOTAL BUY (USD): " + str(total_purchase_usd))
                print("TOTAL BUY DATATYPE: " + str(type(total_purchase)))
                print("BALANCE: " + str(cash_after))
                print("=================================================================")

                # sqlite date time
                # https://www.sqlitetutorial.net/sqlite-date/
                # https://tableplus.com/blog/2018/07/sqlite-how-to-use-datetime-value.html

                # set action
                action = "buy"

                # insert to DB activities table, on buy activity
                db.execute("INSERT INTO activities (user_id, symbol, price, shares, action, cash_before, cash_after, date_time) values (?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))", session["user_id"], symbol, price, shares, action, cash_before, cash_after)

                # update profile spent_cash to true
                db.execute("INSERT INTO profile (user_id, spent_cash, date_time) values (?, 1, datetime('now', 'localtime'))", session["user_id"])

                # When a purchase is complete, redirect the user back to the index page.
                print("\x1b[6;37;41m" + "--------------------------- BUY END ---------------------------" + "\x1b[0m")
                return render_template("/bought.html",symbol=symbol,shares=shares,price=usd(price),total_purchase=usd(total_purchase), cash=usd(cash_after))

        elif spent_cash == 1:
            cash = db.execute("SELECT cash_after FROM activities WHERE user_id = ? ORDER BY date_time DESC LIMIT 1;", session["user_id"])
            # cash is int
            cash_before = cash[0]["cash_after"]

            # get price of share from lookup result
            price = result.get("price")

            # compute total purchase
            total_purchase = float(shares) * price
            # total_purchase = round(total_purchase, 2)

            total_purchase_usd = usd(total_purchase)

            # Render an apology, without completing a purchase, if the user cannot afford the number of shares at the current price
            if total_purchase > cash_before:
                return apology("CAN'T AFFORD")
            else:
                # Compute cash left after purchase
                cash_after = round(float(cash_before) - total_purchase, 2)
                # cash_after = float(cash_before) - total_purchase

                # debug
                print("=================================================================")
                print("USER INPUT")
                print("SYMBOL: " + symbol)
                print("SHARES: " + str(shares))
                print("LOOKUP RETURN")
                print(result)
                print("DATABASE OUTPUT")
                print("ID: "+ str(session["user_id"]))
                print("CURRENT CASH: " + str(cash_before))
                print("CURRENT CASH DATATYPE: " + str(type(cash_before)))
                print("BUY LOGICS")
                print("SHARES: " + str(shares))
                print("PRICE: " + str(price))
                print("TOTAL BUY: " + str(total_purchase))
                print("TOTAL BUY (USD): " + str(total_purchase_usd))
                print("TOTAL BUY DATATYPE: " + str(type(total_purchase)))
                print("BALANCE: " + str(cash_after))
                print("=================================================================")

                # sqlite date time
                # https://www.sqlitetutorial.net/sqlite-date/
                # https://tableplus.com/blog/2018/07/sqlite-how-to-use-datetime-value.html

                # set action
                action = "buy"

                # insert to DB activities table, on buy activity
                db.execute("INSERT INTO activities (user_id, symbol, price, shares, action, cash_before, cash_after, date_time) values (?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))", session["user_id"], symbol, price, shares, action, cash_before, cash_after)

                # When a purchase is complete, redirect the user back to the index page.
                print("\x1b[6;37;41m" + "--------------------------- BUY END ---------------------------" + "\x1b[0m")
                return render_template("/bought.html",symbol=symbol,shares=shares,price=usd(price),total_purchase=usd(total_purchase),cash=usd(cash_after))

    else:
        return render_template("/buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    rows = db.execute("SELECT * FROM activities WHERE user_id = ?", session["user_id"])
    print("\x1b[6;30;42m" + "--------------------------- START HISTORY ---------------------------" + "\x1b[0m")
    print(rows)
    print("\x1b[6;37;41m" + "---------------------------- END HISTORY ----------------------------" + "\x1b[0m")

    return render_template("/history.html", rows=rows)
    # return apology("show_history_transactions","TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        print("\x1b[6;30;43m" + "============================= LOGIN =============================" + "\x1b[0m")
        print(rows)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        session["username"] = rows[0]["username"]

        # Check for first time login

        # currentUID = session["user_id"]

        num_of_login = db.execute("SELECT COUNT(*) FROM profile WHERE user_id = ?", session["user_id"])
        num_of_login = num_of_login[0]["COUNT(*)"]

        if num_of_login == 0:
            db.execute("INSERT INTO profile (user_id, spent_cash, date_time) values (?, 0, datetime('now', 'localtime'))", session["user_id"])
        else:
            spent_cash_check = db.execute("SELECT spent_cash FROM profile WHERE user_id = ? ORDER BY date_time DESC LIMIT 1", session["user_id"])
            spent_cash_check = spent_cash_check[0]["spent_cash"]

            if spent_cash_check == 0:
                db.execute("INSERT INTO profile (user_id, spent_cash, date_time) values (?, 0, datetime('now', 'localtime'))", session["user_id"])
            elif spent_cash_check == 1:
                db.execute("INSERT INTO profile (user_id, spent_cash, date_time) values (?, 1, datetime('now', 'localtime'))", session["user_id"])


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
        print("\x1b[6;30;42m" + "-------------------------- START QUOTE --------------------------" + "\x1b[0m")
        symbol = request.form.get("symbol")

        print("================================================================")
        if (len(symbol) == 0):
            return apology("Missing Symbol")
        elif lookup(symbol) == None:
            return apology("Invalid Symbol")

        result = []
        result = lookup(symbol)
        print("================================================================")

        # check symbol input
        print("CHECK symbol")
        print(symbol)
        print("len(symbol)")
        print(len(symbol))

        # check lookup result
        print("QUOTE RESULT")
        print(result)
        print(len(result))
        price = result.get("price")
        price = usd(price)
        print(price)

        print("\x1b[6;37;41m" + "--------------------------- END QUOTE ---------------------------" + "\x1b[0m")
        return render_template("/quoted.html", result=result,price=price)

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
    if request.method == "POST":
        print("\x1b[6;30;42m" + "--------------------------- SELL START ---------------------------" + "\x1b[0m")
        # get symbol
        symbol = request.form.get("symbol")
        # get shares
        shares_to_sell = request.form.get("shares")
        if len(shares_to_sell) == 0:
            shares_to_sell = 0
        else:
            shares_to_sell = int(shares_to_sell)

        # if user submit without symbol
        if not symbol:
            return apology("Missing Symbol")
        if not shares_to_sell:
            return apology("Missing Shares")

        # db query, based on symbol and shares
        totalshares_current = []
        totalshares_current = db.execute("SELECT *, SUM(shares) as 'totalshares' FROM activities WHERE user_id = ? AND symbol = ?", session["user_id"],symbol)
        totalshares_current_value = totalshares_current[0]["totalshares"]
        # totalshares_current = totalshares_current[0]["totalshares"]
        # if try to sell more shares than user own - throw apology("TOO MANY SHARES")

        # if db query returns empty list
        if (len(totalshares_current) == 0):
            return apology("YOU DON'T HAVE THIS STOCK!")
        elif (len(totalshares_current) == 1):
            if (shares_to_sell > totalshares_current_value):
                return apology("TOO MANY SHARES")
            else:
                # lookup() price of stock
                price = lookup(symbol)
                # print(price.get("price"))
                price = price.get("price")

                # update table
                action = "sell"

                # make shares to negative
                shares_to_sell_neg = (-1 * shares_to_sell)
                shares = shares_to_sell

                # get current cash (i.e. cash_before, cash_after)
                cash = db.execute("SELECT cash_after FROM activities WHERE user_id = ? ORDER BY date_time DESC LIMIT 1;", session["user_id"])

                # cash value to be computed (ie. sell = minus shares, plus cash_before), cash is int
                # total price of shares to be sold
                cash_before = cash[0]["cash_after"]
                total_sell = float(shares) * price

                # update cash_after
                cash_after = cash_before + total_sell

                # check share selling logic
                totalshares_after = totalshares_current_value - shares_to_sell
                print("================================================================")
                print("TOTAL SHARE AFTER")
                print(totalshares_after)
                print("SHARES TO SELL in NEGATIVE")
                print(shares_to_sell * -1)
                print("TOTAL SELL")
                print(total_sell)
                print("SHARES TO SELL neg")
                print(shares_to_sell_neg)
                print("SELL - CASH BEFORE")
                print(cash_before)
                print("SELL - CASH AFTER")
                print(cash_after)
                print("================================================================")

                # insert to DB activities table, on sell activity
                db.execute("INSERT INTO activities (user_id, symbol, price, shares, action, cash_before, cash_after, date_time) values (?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))", session["user_id"], symbol, price, shares_to_sell_neg, action, cash_before, cash_after)

                print("\x1b[6;37;41m" + "--------------------------- SELL END ---------------------------" + "\x1b[0m")

                return render_template("/sold.html", symbol=symbol, shares=shares_to_sell, price=usd(price), total_sell=usd(total_sell), cash=usd(cash_after))

    else:
        # db query, get all unique symbols users own and shares at least 1
        symbolowns = db.execute("SELECT DISTINCT symbol FROM activities WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", session["user_id"])
        symbolowns_list = []
        for i in range(len(symbolowns)):
            symbolowns_list.append(symbolowns[i]["symbol"])
        # print(symbolowns_list)
        # return symbols to sell.html options
        return render_template("/sell.html", symbolowns_list=symbolowns_list)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
