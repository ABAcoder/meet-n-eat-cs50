import os
import re
import random
import smtplib
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
from auto_email import message 
import match

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///meet_n_eat.db")


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
    
    # Gets information about user's bookings which will be inputted in the table
    table = get_table()

    # Renders "index.html" with appropriate information to fill out the table
    return render_template("index.html", size=table["size"], dates=table["dates"], times=table["times"], statuses=table["statuses"], partners=table["partners"], emails=table["emails"])

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username and/or password", 400)

        # Ensure user has confirmed account and email
        if db.execute("SELECT temp_code FROM users WHERE username = ?", request.form.get("username"))[0]["temp_code"] != 0:
            return apology("Must confirm email address", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/forget", methods=["GET", "POST"])
def forget():
    
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST": 
        
        # Check if valid email inputted
        if not request.form.get("email") or len(db.execute("SELECT id FROM users WHERE email = ?", request.form.get("email"))) != 1:
            return apology("Input valid email", 400)

        # Check if email and account has been confirmed
        if db.execute("SELECT temp_code FROM users WHERE email = ?", request.form.get("email"))[0]["temp_code"] != 0:
            return apology("Must confirm email address", 400)

        # Handles the case of forgotten username
        if request.form.get("Login_Info") == "Username":

            # Email containing username is sent to user
            try: 
                # initialize connection to our
                # email server, we will use gmail here
                smtp = smtplib.SMTP('smtp.gmail.com', 587)
                smtp.ehlo()
                smtp.starttls()
                
                # Login with your email and password
                smtp.login('noreplymeetneat@gmail.com', 'TP8umfN>.=-P(}?;')
                
                # Call the message function
                msg = message("Meet and Eat Forgotten Username (Do not reply)", "Hi "+db.execute("SELECT firstname FROM users WHERE email = ?", request.form.get("email"))[0]["firstname"]+", \n\nThis is an automated message. Do not reply. \n\nYour username is: \n\n"+db.execute("SELECT username FROM users WHERE email = ?", request.form.get("email"))[0]["username"]+"\n\nSincerely,\n\nThe Meet and Eat Team")
        
                # Make a list of emails, where you wanna send mail
                to = [request.form.get("email")]
        
                # Provide some data to the sendmail function!
                smtp.sendmail(from_addr="noreplymeetneat@gmail.com", to_addrs=to, msg=msg.as_string())

                # Finally, don't forget to close the connection
                smtp.quit()
            except:
                # If email unable to be sent return error message
                return apology("Email address is invalid", 400)

            # Redirect user to login page
            return redirect("/login")

        # Handles the case of forgotten password
        if request.form.get("Login_Info") == "Password":

            # Generates random 15 digit confirmation code
            temp_code = random.randint(1E15, 1E16-1)

            # Emails user temporary confirmation code
            try: 
                # initialize connection to our
                # email server, we will use gmail here
                smtp = smtplib.SMTP('smtp.gmail.com', 587)
                smtp.ehlo()
                smtp.starttls()
                
                # Login with your email and password
                smtp.login('noreplymeetneat@gmail.com', 'TP8umfN>.=-P(}?;')
                
                # Call the message function
                msg = message("Meet and Eat Forgotten Password (Do not reply)", "Hi "+db.execute("SELECT firstname FROM users WHERE email = ?", request.form.get("email"))[0]["firstname"]+", \n\nThis is an automated message. Do not reply. \n\nYour confirmation code is: \n\n"+str(temp_code)+"\n\nSincerely,\n\nThe Meet and Eat Team")
        
                # Make a list of emails, where you wanna send mail
                to = [request.form.get("email")]
        
                # Provide some data to the sendmail function!
                smtp.sendmail(from_addr="noreplymeetneat@gmail.com", to_addrs=to, msg=msg.as_string())

                # Finally, don't forget to close the connection
                smtp.quit()
            except:
                # Returns error message if email cannot be sent
                return apology("Email address is invalid", 400)

            # Updates users table with temporary confirmation code
            db.execute("UPDATE users SET temp_code = ? WHERE email = ?", temp_code, request.form.get("email"))

            # Sends user to new page
            return render_template("forgotten.html")

    # Renders same page if request method is GET
    else:
        return render_template("forget.html")

@app.route("/forgotten", methods=["POST"])
def forgotten():
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Checks all fields are filled in
        if not request.form.get("username") or not request.form.get("confirm_code") or not request.form.get("new_password") or not request.form.get("confirm_new_password"):
              return apology("Fill in all fields", 400)

        # Check if valid username and corresponding confirmation code inputted
        if len(db.execute("SELECT id FROM users WHERE username = ?", request.form.get("username"))) != 1 or db.execute("SELECT temp_code FROM users WHERE username = ?", request.form.get("username"))[0]["temp_code"] != int(request.form.get("confirm_code")):
            return apology("Input valid username and confirmation code", 400) 

        # Check if new passwords match
        if request.form.get("new_password") != request.form.get("confirm_new_password"):
            return apology("Passwords must match", 400)

        # Saves new hashed password in database
        db.execute("UPDATE users SET hash = ?, temp_code = 0 WHERE username = ?", generate_password_hash(request.form.get("new_password")), request.form.get("username"))

        # Redirects user to login page
        return redirect("/login")
    
    # If page is reached through other means, render same page
    else:
        return render_template("forgotten.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Check if first and last name given
        if not request.form.get("firstname") or not request.form.get("lastname"):
            return apology("must give full name", 400)

        # Check if valid college.harvard.edu email inputted
        if not request.form.get("email") or not re.search("^.+@college\.harvard\.edu$", request.form.get("email")):
            return apology("must provide valid Harvard College email", 400)
        
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("must provide password", 400)

        # Query database for username or email
        elif db.execute("SELECT username FROM users WHERE username = ?", request.form.get("username")) or db.execute("SELECT email FROM users WHERE email = ?", request.form.get("email")):
            return apology("username or email already used", 400)

        # Check if passwords match
        elif not(request.form.get("password") == request.form.get("confirmation")):
            return apology("passwords do not match", 400)

        # Generate random 15 digit confirmation code
        temp_code = random.randint(1E15, 1E16-1)

        # Send email with confirmation code
        try: 
            # initialize connection to our
            # email server, we will use gmail here
            smtp = smtplib.SMTP('smtp.gmail.com', 587)
            smtp.ehlo()
            smtp.starttls()
            
            # Login with your email and password
            smtp.login('noreplymeetneat@gmail.com', 'TP8umfN>.=-P(}?;')
            
            # Call the message function
            msg = message("Meet and Eat Confirmation Code (Do not reply)", "Hi "+request.form.get("firstname")+", \n\nThis is an automated message. Do not reply. \n\nThank you for signing up for Meet&Eat! We are glad to have you! \n\nYour confirmation code is:\n\n"+str(temp_code)+"\n\nSincerely,\n\nThe Meet and Eat Team")
    
            # Make a list of emails, where you wanna send mail
            to = [request.form.get("email")]
    
            # Provide some data to the sendmail function!
            smtp.sendmail(from_addr="noreplymeetneat@gmail.com", to_addrs=to, msg=msg.as_string())

            # Finally, don't forget to close the connection
            smtp.quit()
        except:
            return apology("Email address is invalid", 400)

        # Update database with user inputted information
        db.execute("INSERT INTO users (username, hash, email, firstname, lastname, temp_code) VALUES (?,?,?,?,?,?)", request.form.get("username"),  generate_password_hash(request.form.get("password")), request.form.get("email"), request.form.get("firstname"), request.form.get("lastname"), temp_code)

        # Redirect user to new page to confirm account and email
        return redirect("/registered")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/registered", methods=["GET", "POST"])
def registered():
    """Registered"""

    # Forget any user_id
    session.clear()
    
    # Code implemented when request method is POST
    if request.method == "POST": 

        # Check to see if user is attempting to resend the confirmation code potentially to new email
        if request.form.get("username") == None and request.form.get("confirm_code") == None:

            # Check if proper fields are filled in
            if not request.form.get("new_email_username") or not request.form.get("new_email_password") or not re.search("^.+@college\.harvard\.edu$", request.form.get("new_email_email")):
                return apology("Must provide username, password, and valid email. Reload page.", 400)

            # Check if email provided already in use (besides the email of the user)
            if len(db.execute("SELECT * FROM users WHERE email = ? AND username <> ?", request.form.get("new_email_email"), request.form.get("new_email_username"))) != 0:
                 return apology("Email already in use. Reload page.", 400)

            # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("new_email_username"))

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("new_email_password")):
                return apology("Invalid username and/or password. Reload page.", 400)

            # Email to resend confrimation code 
            try: 
                # initialize connection to our
                # email server, we will use gmail here
                smtp = smtplib.SMTP('smtp.gmail.com', 587)
                smtp.ehlo()
                smtp.starttls()
                
                # Login with your email and password
                smtp.login('noreplymeetneat@gmail.com', 'TP8umfN>.=-P(}?;')
                
                # Call the message function
                msg = message("Meet and Eat Confirmation Code (Do not reply)", "Hi "+db.execute("SELECT firstname from users WHERE username = ?", request.form.get("new_email_username"))[0]["firstname"]+", \n\nThis is an automated message. Do not reply. \n\nThank you for signing up for Meet&Eat! We are glad to have you! \n\nYour confirmation code is:\n\n"+str(db.execute("SELECT temp_code from users WHERE username = ?", request.form.get("new_email_username"))[0]["temp_code"])+"\n\nSincerely,\n\nThe Meet and Eat Team")
        
                # Make a list of emails, where you wanna send mail
                to = [request.form.get("new_email_email")]
        
                # Provide some data to the sendmail function!
                smtp.sendmail(from_addr="noreplymeetneat@gmail.com", to_addrs=to, msg=msg.as_string())

                # Finally, don't forget to close the connection
                smtp.quit()
            except:
                # Handle potential errors from failure to send email
                return apology("Email address is invalid", 400)

            # Replace email of user with new inputted email
            db.execute("UPDATE users SET email = ? WHERE username = ?", request.form.get("new_email_email"),request.form.get("new_email_username"))

            # Return to page so that account can be confirmed
            return redirect("/registered")

        # Check to see if user is attempting to confirm account and email
        if request.form.get("new_email_username") == None and request.form.get("new_email_password") == None and request.form.get("new_email_email") == None:

            # Check username
            if len(db.execute("SELECT temp_code FROM users WHERE username = ?", request.form.get("username"))) == 0:
                return apology("Invalid username", 400)
            
            # Check to see if confirmation code inputted corresponds to user's confirmation code
            if db.execute("SELECT temp_code FROM users WHERE username = ?", request.form.get("username"))[0]["temp_code"] == int(request.form.get("confirm_code")):
                db.execute("UPDATE users SET temp_code = 0 WHERE username = ?", request.form.get("username"))
                return redirect("/login")

            # If the corresponding confirmation code does not match with anything, then username or code is invalid 
            return apology("Invalid code or username", 400)

        # If inputs do not fall in two previous cases, user misread directions
        return apology("Re-read the directions and reload the page.", 400)

    # Return rendered page if request method is GET
    else:
        return render_template("registered.html")

# Global variable to be used in "/match" and "/hours"
meal_date = "01/01/2000"

# Webpage with form that lets the user select a date and meal type for the booking they wish to make
@app.route("/match", methods=["GET", "POST"])
@login_required
def matched():
    # When form is submitted
    if request.method == "POST":

        # Ensure user inputted all required values into the form
        if not request.form.get("date") or not request.form.get("meal"):
            return apology("Input date and meal", 400)
        
        # Gets date of booking (as datetime.datetime object) and meal type (as string)
        date = datetime.datetime.strptime(request.form.get("date"), "%Y-%m-%d")
        meal = request.form.get("meal")

        # Ensures user submitted a date that is not in the past (i.e. not before today)
        if date + datetime.timedelta(hours=23, minutes=59, seconds=59) < datetime.datetime.today():
            return apology("Input valid date", 400)

        # Ensures user submitted a meal type appropriate for the weekday of the selected date, in accordance to
        # the HUDS dining schedule. Specifically, an apology is returned when
        # 1) The user selects "Brunch" with Monday - Friday
        # 2) The user selects "Lunch" for Saturday and Sunday
        # 3) The user selects "Breakfast" for Sunday
        # 4) The user selects "Continental Breakfast" for Monday - Saturday
        if (date.weekday() in range(5) and meal == "Brunch") or (date.weekday() in range(5,7) and meal == "Lunch") or (date.weekday() == 6 and meal == "Breakfast") or (date.weekday() in range(6) and meal == "Continental Breakfast"):
             return apology("Input valid date and meal", 400)

        # times stores all potential times (in 15 minute increments) corresponding to each meal type.
        # For instance, since Breakfast is from 7:30 a.m. to 10:30 a.m., times will store the times 
        # 7:30 a.m., 7:45 a.m., 8:00 a.m., 8:15 a.m., ... , 9:45 a.m., 10:00 a.m., 10:15 a.m., 10:30 a.m.
        # times is used later to provide information when rendering the next template
        if meal == "Breakfast":
            times = [datetime.timedelta(hours=7, minutes=30) + datetime.timedelta(minutes=(15 * x)) for x in range(13)]
        elif meal == "Continental Breakfast":
            times = [datetime.timedelta(hours=7, minutes=30) + datetime.timedelta(minutes=(15 * x)) for x in range(11)]
        elif meal == "Brunch":
            times = [datetime.timedelta(hours=11, minutes=30) + datetime.timedelta(minutes=(15 * x)) for x in range(11)]
        elif meal == "Lunch":
            times = [datetime.timedelta(hours=11, minutes=30) + datetime.timedelta(minutes=(15 * x)) for x in range(13)]
        elif meal == "Dinner":
            times = [datetime.timedelta(hours=16, minutes=30) + datetime.timedelta(minutes=(15 * x)) for x in range(13)]
        
        # Converts each element in times from datetime.timedelta to string, formatted in the form "hh:mm a.m./p.m."
        n = len(times)
        for i in range(n):
            times[i] = str(times[i])[:-3]

        # Stores the meal date into global variable "meal_date", so it can be used by the function "hours()" when
        # the user inputs the hours of the booking 
        global meal_date
        meal_date = date.strftime("%m/%d/%Y")

        # Returns "hours.html", a webpage displaying the form for the user to select the specific start and end times 
        # for the booking
        return render_template("hours.html", date=meal_date, meal=meal, times=times)
    
    else:
        # Renders "match.html" if user got to page via "GET"
        return render_template("match.html")


# Page immediately succeeding "match.html" that includes a form for the user to input the specific start/end time
# that they wish to make a booking for 
@app.route("/hours", methods=["GET", "POST"])
@login_required
def hours():
    # When form is submitted
    if request.method == "POST":
        
        # Gets start time and end time from form as datetime.datetime objects
        start = datetime.datetime.strptime(meal_date+"T"+request.form.get("start"), "%m/%d/%YT%H:%M")
        end = datetime.datetime.strptime(meal_date+"T"+request.form.get("end"), "%m/%d/%YT%H:%M")
        
        # Ensures that the starttime is not in the past (ex. user can not schedule a meal for today at 5:00 p.m.
        # if it is already 6:00 p.m.)
        if start < datetime.datetime.today():
            return apology("Input valid date", 400)

        # Ensures that the difference in times is more than 30 minutes, since bookings must be longer than or
        # equal to 30 minutes
        if end - start < datetime.timedelta(minutes = 30):
            return apology("Availability must at least 30 minutes long", 400)
        
        # Enters the booking that the user made into the queue with stauts 'PENDING'
        match.add_queue(start.strftime("%m/%d/%Y %H:%M"), end.strftime("%m/%d/%Y %H:%M"), session["user_id"])

        # Runs the matching algorithm in match.py, which will match the user with another user if their bookings
        # have times that overlap
        match.match()

        # User is redirected to the homepage, where user's updated list of bookings is displayed
        return redirect("/")
    
    else:
        # Since the user must submit the prior form ("match.html") in order to complete the form in "hours.html",
        # if the user reaches "/hours" via "GEt" (by typing the url, etc.) they are redirected to "/match"
        return redirect("/match")

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    
    # CHeck if request method is POST
    if request.method == "POST":
        
        # Check to see if relevant fields are filled
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("new_name"):
            return apology("Input name, username, and passcode", 400)
        
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Change first name if selected option was first name
        if request.form.get("name") == "First_Name": 
            db.execute("UPDATE users SET firstname = ? WHERE id = ?", request.form.get("new_name"), session["user_id"])

        # Change last name if selected option was last name
        if request.form.get("name") == "Last_Name": 
            db.execute("UPDATE users SET lastname = ? WHERE id = ?", request.form.get("new_name"), session["user_id"])

        # Reload page profile page
        return redirect("/profile")
    
    # Update information when request method is GET
    else:
        user_info = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        return render_template("profile.html", first_name = user_info[0]["firstname"], last_name = user_info[0]["lastname"], username = user_info[0]["username"], email = user_info[0]["email"])

# Page which lets user cancel bookings that the user has already made
@app.route("/cancel", methods=["GET", "POST"])
@login_required
def canceling():

    # When the user fills out the form
    if request.method == "POST":
        # Cancels the booking using the "cancel()" function in "match.py"
        match.cancel(request.form.get("cancel"))

        # Redirects user to homepage after booking is cancelled to display updated table of bookings
        return redirect("/")
    
    else:
        # Gets information used to fill out the form in "cancel.html"
        table = get_table()

        # Renders "cancel.html", a table of current bookings of the user with the option to "cancel" next to each entry
        return render_template("cancel.html", size=table["size"], dates=table["dates"], times=table["times"], statuses=table["statuses"], partners=table["partners"], emails=table["emails"], q_ids=table["q_ids"])


# Gets data required to populate tables in "/" and "/cancel" with information about each booking that the user has made 
def get_table():
    # Selects all entries in queue booked by the user
    meets = db.execute("SELECT * FROM queue WHERE user_id = ? ORDER BY start", session["user_id"])

    # Gets the date of each booking
    dates = [meet["start"].split(' ')[0] for meet in meets]

    # Gets the start and end times for each booking, storing it as "start - end" in the list 'times'
    starts = [meet["start"].split(' ')[1] for meet in meets]
    ends = [meet["end"].split(' ')[1] for meet in meets]
    times = [match.am_pm(starts[i]) + " - " + match.am_pm(ends[i]) for i in range(len(starts))]

    # Gets the status (i.e. "PENDING" or "MATCHED") for each booking
    statuses = [meet["status"] for meet in meets]

    # Initiates partner_ids, which:
    # If the booking is already matched, stores the user id number of the partner that the user is matched with
    # If the booking is still pending, stores "" (empty)
    partner_ids = []
    for meet in meets:
        if meet["partner"] == None:
            partner_ids.append("")
        else:
            partner_ids.append(meet["partner"])
    
    # Initiates users_first, which:
    # If the booking is already matched, stores the first name of the partner that the user is matched with
    # If the booking is still pending, stores "" (empty)
    users_first = []
    for u_id in partner_ids:
        if u_id == "":
            users_first.append("")
        else:
            users_first.append(db.execute("SELECT * FROM users WHERE id = ?", u_id)[0]["firstname"])
    
    # Initiates users_last, which:
    # If the booking is already matched, stores the last name of the partner that the user is matched with
    # If the booking is still pending, stores "" (empty)
    users_last = []
    for u_id in partner_ids:
        if u_id == "":
            users_last.append("")
        else:
            users_last.append(db.execute("SELECT * FROM users WHERE id = ?", u_id)[0]["lastname"])

    # Initiates partners, which includes the full name of the partners in each booking (empty if not matched)
    partners = [users_first[i] + " " + users_last[i] for i in range(len(users_first))]

    # Initiates emails, which:
    # If the booking is already matched, stores the email of the partner that the user is matched with
    # If the booking is still pending, stores "" (empty)
    emails = []
    for u_id in partner_ids:
        if u_id == "":
            emails.append("")
        else:
            emails.append(db.execute("SELECT * FROM users WHERE id = ?", u_id)[0]["email"])

    # Gets the q_id (primary id of queue table) for each booking 
    q_ids = [q_id["q_id"] for q_id in meets]
    
    # Returns a dictionary with each key corresponding to the lists declared above
    return {"size":len(meets), "dates":dates, "times":times, "statuses":statuses, "partners":partners, "emails":emails, "q_ids":q_ids}

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
