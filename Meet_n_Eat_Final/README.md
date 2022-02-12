Meet&Eat 
Movie
https://drive.google.com/file/d/1FqXHUU2UiCrX13OfHOnBsoQK9-wlF49N/view?usp=sharing

How to the Run the Application
This project can be run on either the online version or desktop version of Visual Studio Code. If you would like to run this application on the desktop version of Visual Studio Code, start from step 1. If you will use the online version, log in to the online version and start from step 3.
1. Download the desktop version of Visual Studio Code.
2. In the terminal, install the packages ‘cs50’ ‘Flask’ ‘Flask-Session’ and ‘datetime’ using pip3. These packages are also found in ‘requirements.txt’ within the ‘Meet_n_Eat_Final’ directory.
        To install cs50 run

 $ pip3 install cs50


		To install Flask run

 $ pip3 install Flask


		To install Flask-Session run

 $ pip3 install Flask-Session


		To install datetime run

 $ pip3 install datetime


If pip3 is not installed, then run

 $ sudo apt-get -y install python3-pip


		and verify its installation by running

 $ pip3 --version


3. Place the “Meet_n_Eat_Final” folder in your codespace and type the following command “cd Meet_n_Eat_Final”
4. Then, type “flask run” in the terminal and paste the output link into a browser.

Registering an Account
 
On the login page, click the “Register” link at the top of the navigation bar. Provide the following personal- first name, last name, and a unique, valid “college.harvard.edu” email-  and create a unique username (which cannot be changed) and password (which must be confirmed). 

When the “Register” button is clicked, the user will be guided to a new page and an email containing a randomly generated confirmation code will be sent to the email address the user provided from noreplymeetneat@gmail.com. Once the user receives the code, they must fill out the first two fields of the “Confirm Code” page with their username and confirmation code, leave the rest of the fields blank, and click the “Confirm Account” button. If the code must be resent to them or the email address they provided was incorrect, they must fill out the last three fields of the “Confirm Code” page with their username, password, and desired “college.harvard.edu” email leave the rest of the fields blank, and click the “Resend Code” button. The confirmation code will be sent to the email address provided on the “Confirm Code” page and the website will consider this new email address as the user’s email address.

After successfully registering an account, a user will be guided back to the login page and will be able to log in to their account.


Logging In/Out

On the login page (which can be navigated to by pressing the “Log In” link at the top of the navigation bar), a user must provide a valid username and password. A user will not be able to log in if they have not confirmed their account. Once logged in, a user can log out of their account if they click the “Log Out” link at the top of the navigation bar.  


Recovering Forgotten Username and/or Password

On the login page (which can be navigated to by pressing the “Log In” link at the top of the navigation bar), a user can recover forgotten login credentials by pressing the “Forgot Username or Password?” link. The user will be redirected to another page which will ask them to indicate whether they have forgotten their username or password by selecting the corresponding choices on the web page select menu. They must then provide their corresponding account email address and press the “Submit” button.

If a user has forgotten their username, an email will be sent to their account email address containing their username from noreplymeetneat@gmail.com. If a user has forgotten their password, an email will be sent to their account email address containing a confirmation code from noreplymeetneat@gmail.com and they will be sent to a new page to reset their password. On this page with the header “Reset Password,” the user must provide their username and their confirmation code, create a password and confirm it in a second password field, and press the “Reset Password” button in order to reset their password. They will then be redirected to the login page.


Homepage

Once logged in, the first page which comes to view is the homepage, in the directory “/”. The homepage displays all current bookings that the user has made in a table, ordered by the status of the booking and chronological order of the booking time. 

If the status of the booking is PENDING, then the table displays the date of the booking under ‘Date,’ the time range that the user signed up for under ‘Time,’ and the status of the booking under ‘Status’ which displays “PENDING;” the other columns (‘Matched With’ and ‘Email’) are left blank while the status is pending as the user waits for another student to enter the queue with overlapping dates and times. 

If the status of the booking is MATCHED, then the table displays the date of the matched booking under ‘Date,’ the time range of the actual meeting under ‘Time’(rather than the time range that the user initially signed up for since these can differ based on the availability of the partner), the status of the booking which displays “MATCHED” under ‘Status,’ the name of the student that the user has been matched with under ‘Matched With,’ and the email of the student the user has been matched with under ‘Email.’


Booking a Meetup

To book a meetup with another student, the user clicks on ‘Meetups’ listed in the Navbar on the top left of the webpage; this opens a dropdown menu with options ‘Book Meetup’ and ‘Cancel Meetup.’ By clicking on ‘Book Meetup,’ the user is redirected to the “/match” directory, where the user is able to input the information required to schedule the meetup, specified below.

In the “/match” page, the user is able to select the date of the meetup and type of meal that they wish to book for. Under the “Date:” input menu, the user is able to type in a date in “mm/dd/yyyy” format, or the user can click on the small calendar icon to select and click on a date from the calendar input. Under the “Meal:” dropdown menu, the user is able to select the type of meal they wish to book for, the options being “Breakfast,” “Continental Breakfast,” “Lunch,” “Brunch,” “Dinner.” Once the appropriate date and meal is selected, the user is then able to press “Book” and be redirected to a page where they can input the specific time of the meal. 

However, different types of meals are served on different days of the week at Annenberg; for instance, Continental Breakfast is only served on Sundays. It is contingent on the user to select an appropriate type of meal for the day of the week they are booking an appointment for; if the user submits an incorrect combination of the date and the type of meal, for instance booking for Continental Breakfast on a Monday, then an error message prompting the user to “Input Valid Date and Meal” is raised. However, in order for the user to If the user presses “Book” without selecting a date and/or type of meal, an error message is raised prompting the user to “Input Date and Meal.” If the user enters a past date into the form and submits, an error message is raised prompting the user to “Input Valid Date.” 

Once the user successfully navigates past the “Book Meetup” page, they are taken to a webpage with a form titled “Availability,” which prompts the user to “Select availability for” the meal they selected. The user is able to select the start time and end time of their availability using dropdown menus each under “Start:” and “End:” respectively. The available time options are listed in 15 minute increments. The dropdown times change based on the type of meal that the user inputted previously, so that the options are in the range of the actual time of the meal; for instance, if the user selects Continental Breakfast, then times from 7:30 a.m. to 10:00 a.m. are listed in the dropdown. Once the user selects a start and end time, the user is able to select “Submit,” placing their booking in the queue.

If the user inputs a time that is already past the start time, for instance if they select dinner and input “5:00 p.m.” for the start time at 5:15 p.m., then an error message is raised prompting the user to “input valid date.” If the user inputs a combination of start and end times such that the end time comes before the start time, or if an user inputs a time range that is less than or equal to 15 minutes, then an error message is raised displaying that “availability must be at least 30 minutes long.”

Once the user’s booking is placed in the queue, the user is redirected to the homepage and the matching algorithm is run. If there exists another user in the queue such that there is a time overlap of 30 or more minutes for each users’ bookings, then the user’s booking will be displayed in the homepage with a status of  “MATCHED,” with the matched student’s name and email visible, as well as the actual meeting time calculated based on the two users’ respective availabilities. If there exists no other users in the queue with overlapping times for the bookings, then the user’s booking is displayed in the homepage with a status of “PENDING.” 

If the user’s status is “PENDING,” then the user can navigate away from the page and wait for their booking to be matched; once a match is found, an automated email is sent to both users detailing the specifics of the meeting, including the name of the person who the user was matched with, and the date and time of the meeting that is calculated based on the availability of the two users. 


Cancelling a Meetup

After the user schedules a booking, the user is able to cancel their booking(s) if the user becomes unavailable during their priorly scheduled times. To cancel a meetup with another student, the user clicks on ‘Meetups’ listed in the Navbar on the top left of the webpage; this opens a dropdown menu with options ‘Book Meetup’ and ‘Cancel Meetup.’ By clicking on ‘Cancel Meetup,’ the user is redirected to the “/cancel” directory, where the user is able to select which bookings to cancel.

In the “/cancel” page, a table listing all current bookings of the user similar to that in the homepage is displayed, with a “cancel” button next to each entry of the table. The user is able to cancel any meeting, regardless of whether or not its status is “PENDING” or “MATCHED,” by simply clicking on the “cancel” button corresponding to the booking in the table which the user wishes to cancel. After selecting cancel, the user is redirected to the homepage, and if the booking is removed successfully then it will be removed from the table. 

If the status of the cancelled booking is “PENDING,” then the booking is simply removed from the table of the user, and the pending booking is taken out of the queue of bookings waiting to be matched.

If the status of the cancelled booking is “MATCHED,” then the booking is removed from the table of the user and the table of the matched user. Additionally, in the case that an already matched booking is cancelled by one of the users, an automated email is sent to both users in the match notifying them that the booking has been cancelled; the email contains information about who cancelled the booking and the time that the booking was originally scheduled for. 


Profile Page

Once logged in, a user can navigate to their profile page by clicking the “Account” link at the top of the navigation bar and pressing the “Profile” link in the corresponding dropdown. On the “Profile” page, a user can view their first name, last name, username, and email. They can also edit their first or last name by selecting “First Name” or “Last Name” in the select menu, inputting a new last name or first name in the “Input New Name” text field, providing their username and password in the corresponding username and password fields respectively, and pressing the “Change” button. They will see these changes after pressing the “Change” button on the reloaded “Profile” page.
