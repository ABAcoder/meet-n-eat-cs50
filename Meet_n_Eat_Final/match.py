import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

import datetime
import smtplib
from auto_email import message 

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///meet_n_eat.db")


# Match users based on overlapping availabilities, and calculates the time of the meeting
# Updates database when a match is found, and notifies users via email when they are matched
def match():
    # Get all bookings which has status 'PENDING' in chronological order of start time
    queue = db.execute("SELECT * FROM queue WHERE status = 'PENDING' ORDER BY start")

    # If there are less than 2 bookings waiting to be matched, no match can be made
    length = len(queue)
    if length < 2:
        print("Match ended 1")
        return False
    
    # Initiates list of potential times of each booking, the dates of each of the bookings,
    # and the id number corresponding to the user that submitted each booking.
    # For instance, the 0th entry of pot_times, date, and user_ids corresponds to the set of potential times
    # that the user is available for, the date of the booking, and the id number of the user, respectively 
    # corresponding to the earliest booking in the queue
    pot_times = []
    date = []
    user_ids = []

    for user in queue:
        start = get_datetime(user["start"])
        # Initiates set of times in increments of 15 minutes that the particular booking in the queue is available for 
        set_times = [start + datetime.timedelta(minutes=((x)*15)) for x in range(get_increments(user["start"], user["end"]))]
        # The i-th entry of pot_times corresponds to the list set_times corresponding to the i-th booking in the queue
        pot_times.append(set_times)
        date.append(get_date(user["start"]))
        user_ids.append(user["user_id"])
    
    # Compares the set of potential times that each booking is available for, and stores the indices of the queue
    # corresponding to each booking into variables "k" and "l" if a non-trivial match is found. 
    # A non-trivial match is a match such that 
    # 1) the intersection of potential times is greater than or equal to 30 minutes (so that meeting times are 
    # longer than or equal to 30 minutes) 
    # 2) the intersection is not empty 
    # 3) the dates corresponding to each booking are the same (so that two bookings on different dates but same
    # times do not get matched) 
    # 4) the users who made each booking are different (so that a user is not matched with hemselves) and 
    # 5) the two booking are non-identical (so that a booking does not match with the same booking)
    # For instance, if users in the 0th and 3rd entries of the booking 
    k = -1
    l = -1
    for j in range(length):
        for i in range(j, length):
            # List that stores the intersection of available times in bookings "i" and "j"
            cap_times = [t for t in pot_times[j] if t in pot_times[i]]

            # Checks if the list is non-trivial, each conditional checking statements 1, 2, 3, 4, and 5 respectively
            if not (len(cap_times) < 3 or cap_times == [] or date[j] != date[i] or user_ids[j] == user_ids[i] or i == j):
                # If non-trivial, stores the values of "j" and "i" into "k" and "l" respevtively, and terminates the loop
                k = j
                l = i
                break
        # Outer loop terminates if match is found and the value of "k" is set to "j"
        if k == j:
            break

    # If the loop ends without any match being found, the function returns False
    if k == -1:
        return False

    # Find the q_id (primary key of queue table) and the user_id (primary key of users table) corresponding to the indices of
    # queue that were matched, stored in "k" and "l".  
    q1 = int(queue[k]["q_id"])
    u1 = int(queue[k]["user_id"])

    q2 = int(queue[l]["q_id"])
    u2 = int(queue[l]["user_id"])

    # Gets the calculated start and end times of the meeting and formats it as a string. The values are equivalent 
    # to the start and end times of the non-trivial intersection which we found above
    start = (date[k] + " " + str(cap_times[0]))[:-3]
    end = (date[k] + " " + str(cap_times[-1]))[:-3]

    # Updates the database, changing the status of each booking to 'MATCHED,' updating the times of the booking to the 
    # actual time of the meeting, and including the user_id of the partner (in column "partner") and the q_id of the matched
    # queue (in column "match") 
    db.execute("UPDATE queue SET (status, partner, start, end, match) = ('MATCHED', ?, ?, ?, ?) WHERE q_id = ?", u2, start, end, q2, q1)
    db.execute("UPDATE queue SET (status, partner, start, end, match) = ('MATCHED', ?, ?, ?, ?) WHERE q_id = ?", u1, start, end, q1, q2)

    # Queries the "users" table in the database to get information about the users from their user_id that we previously
    # determined as u1 and u2.
    user1 = db.execute("SELECT firstname, lastname, email FROM users WHERE id = ?", u1)[0]
    user2 = db.execute("SELECT firstname, lastname, email FROM users WHERE id = ?", u2)[0]

    # Sends an automated email to the two users when they are matched, which includes information about the name
    # of the user whom they were matched with and the date and time of the meeting calculated based on their availability
    try: 
        # initialize connection to our
        # email server, we will use gmail here
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
            
        # Login with your email and password
        smtp.login('noreplymeetneat@gmail.com', 'TP8umfN>.=-P(}?;')
        
        # Sending a message to user1
        # Call the message function
        msg = message("You've been Matched!", "Hi "+ user1["firstname"] +", \n\nThis is an automated message. Do not reply. \n\nThanks for scheduling a meal with us. We've found a match!  \n\nYou'll be meeting: "+ user2["firstname"] + " " + user2["lastname"] +"\n\nYour meal time is: " + start.split(' ')[0] + " from " + start.split(' ')[1] + " to " + end.split(' ')[1] + "\n\n Thanks for using us, and enjoy your meal! \n\nSincerely,\n\nThe Meet and Eat Team")
    
        # Make a list of emails, where you wanna send mail
        to = [user1["email"]]

        # Provide some data to the sendmail function!
        smtp.sendmail(from_addr="noreplymeetneat@gmail.com", to_addrs=to, msg=msg.as_string())

        # Sending a message to user2
        # Call the message function
        msg = message("You've been Matched!", "Hi "+ user2["firstname"] +", \n\nThis is an automated message. Do not reply. \n\nThanks for scheduling a meal with us. We've found a match!  \n\nYou'll be meeting: "+ user1["firstname"] + " " + user1["lastname"] +"\n\nYour meal time is: " + start.split(' ')[0] + " from " + start.split(' ')[1] + " to " + end.split(' ')[1] + "\n\n Thanks for using us, and enjoy your meal! \n\nSincerely,\n\nThe Meet and Eat Team")
    
        # Make a list of emails, where you wanna send mail
        to = [user2["email"]]

        # Provide some data to the sendmail function!
        smtp.sendmail(from_addr="noreplymeetneat@gmail.com", to_addrs=to, msg=msg.as_string())

        # Finally, don't forget to close the connection
        smtp.quit()

    except:
        return apology("Email address is invalid", 400)


# Inserts a booking with 'PENDING' status into the queue table, based on given start & end times and the id of the user
# who made the booking
def add_queue(start, end, user_id):
    db.execute("INSERT INTO queue (start, end, user_id, status) VALUES (?, ?, ?, 'PENDING')", start, end, user_id)


# Returns the number of 15 minute increments given a time range specified by its start and end time. 
# For instance, if start = 7:00 and end = 8:15, then the 15 minute increments which can be made are the times
# 7:00, 7:15, 7:30, 7:45, 8:00, and 8:15, so it will return 5.
def get_increments(start, end):
    start_time = hour(start) * 4 + minute(start) / 15
    end_time = hour(end) * 4 + minute(end) / 15
    
    return int(end_time - start_time + 1)


# Cancels a booking, deleting the booking from the queue. If the booking is already matched, then the partner's booking
# is also deleted from the queue; in this case, an automated email is sent to both users notifying them of the cancellation
def cancel(q_id):
    # Gets the booking with the particular q_id (the primary key of the queue table)
    book = db.execute("SELECT * FROM queue WHERE q_id = ?", q_id)[0]
    
    # If the booking does not have a partner, i.e. the booking has not been matched yet, then the booking is 
    # simply removed from the queue
    if book["partner"] == None:
        db.execute("DELETE FROM queue WHERE q_id = ?", q_id)

    # Otherwise (i.e. the booking is matched), bookings made by both the user and their partner are deleted from the database,
    # and an automated email notification is sent to both users
    else:
        # From the users table, selects information about the user and the partner of the cancelled booking
        user1 = db.execute("SELECT * FROM users WHERE id = ?", book["user_id"])[0]
        user2 = db.execute("SELECT * FROM users WHERE id = ?", book["partner"])[0]
        
        # Removes the booking cancelled by the user. Since the booking is matched, the partner's booking is also
        # removed from the queue
        db.execute("DELETE FROM queue WHERE q_id = ?", book["match"])
        db.execute("DELETE FROM queue WHERE q_id = ?", q_id)

        # Gets the start and end times of the cancelled meeting
        start = book["start"]
        end = book["end"]

        # Sends an automated email to the two users of the cancelled match, which includes information about the user who 
        # cancelled the booking, the names of the users in the meeting, and the originally planned date and time of the meeting 
        try: 
            print("Entered Try")
            # initialize connection to our
            # email server, we will use gmail here
            smtp = smtplib.SMTP('smtp.gmail.com', 587)
            smtp.ehlo()
            smtp.starttls()

            print("Checkpoint 1")
            # Login with your email and password
            smtp.login('noreplymeetneat@gmail.com', 'TP8umfN>.=-P(}?;')

            print("Checkpoint 2")
            #To user1
            # Call the message function
            msg = message("Your Booking has been Cancelled", "Hi "+user1["firstname"]+", \n\nThis is an automated message. Do not reply. \n\nThanks for scheduling a meal with us. The following meal has been cancelled by "+user1["firstname"] + "\n\nYou'll be meeting: "+user2["firstname"]+ " " + user2["lastname"] +"\n\nYour meal time is: " + start.split(' ')[0] + " from " + start.split(' ')[1] + " to " + end.split(' ')[1] + "\n\n Please feel free to book another meal. \n\nSincerely,\n\nThe Meet and Eat Team")

            print("Checkpoint 3")
            # Make a list of emails, where you wanna send mail
            to = [user1["email"]]

            print("Checkpoint 4")
            # Provide some data to the sendmail function!
            smtp.sendmail(from_addr="noreplymeetneat@gmail.com", to_addrs=to, msg=msg.as_string())

            # To user2
            # Call the message function
            msg = message("Your Booking has been Cancelled", "Hi "+ user2["firstname"] +", \n\nThis is an automated message. Do not reply. \n\nThanks for scheduling a meal with us. The following meal has been cancelled by " + user1["firstname"] + "\n\nYou'll be meeting: "+ user1["firstname"] + " " + user1["lastname"] +"\n\nYour meal time is: " + start.split(' ')[0] + " from " + start.split(' ')[1] + " to " + end.split(' ')[1] + "\n\n Please feel free to book another meal. \n\nSincerely,\n\nThe Meet and Eat Team")

            # Make a list of emails, where you wanna send mail
            to = [user2["email"]]

            # Provide some data to the sendmail function!
            smtp.sendmail(from_addr="noreplymeetneat@gmail.com", to_addrs=to, msg=msg.as_string())

            # Finally, don't forget to close the connection
            smtp.quit()
        except:
            return apology("Email address is invalid", 400)


# Takes a string formatted as "mm/dd/yyyy hh:mm:ss" and returns a string formatted as "mm/dd/yy"
def get_date(time):
    return datetime.datetime(year=year(time), month=month(time), day=day(time)).strftime("%m/%d/%Y")


# Takes a string formatted as "hh:mm:ss" and returns a datetime.timedelta object of corresponding hour and minute values
def get_datetime(time):
    return datetime.timedelta(hours = hour(time), minutes = minute(time))


# Takes a string formatted as "mm/dd/yyyy hh:mm:ss" and returns the value of yyyy as an integer
def year(time):
    return int(time.split(" ")[0].split("/")[2])


# Takes a string formatted as "mm/dd/yyyy hh:mm:ss" and returns the value of mm as an integer
def month(time):
    return int(time.split(" ")[0].split("/")[0])


# Takes a string formatted as "mm/dd/yyyy hh:mm:ss" and returns the value of dd as an integer
def day(time):
    return int(time.split(" ")[0].split("/")[1])


# Takes a string formatted as "mm/dd/yyyy hh:mm:ss" and returns the value of hh as an integer
def hour(time):
    return int(time.split(" ")[1].split(":")[0])


# Takes a string formatted as "mm/dd/yyyy hh:mm:ss" and returns the value of mm as an integer
def minute(time):
    return int(time.split(" ")[1].split(":")[1])


# Given a string formatted as "hh:mm:ss" in miltary (24 hour) time, returns a string formatted to the corresponding
# "hh:mm:ss a.m./p.m." time value
def am_pm(time):
    hour = int(time.split(":")[0])
    minute = time.split(":")[1]

    meridiem = " a.m." if int(hour/12) == 0 else " p.m."
    if hour == 12:
        return "12:" + str(minute) + meridiem
    else:
        return str(hour % 12) + ":" + str(minute) + meridiem 