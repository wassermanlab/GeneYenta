	TODO.md	GeneYenta	Aug. 30, 2013
		
			by Zach Maurer

=== Description ====
	Here is a list of all possible project TODOs.
	- They are organized by functional similarity.
	- More important/time-intensive tasks are indicated with a '++'
	- Less " " tasks are indicated with a '+'
	- Use @WIP: [person doing the work] to indicate who is working on it at the moment. (Or use Asana)
=== end ===
		
=== Index of TODO Categories ===
	1. Security
	2. Testing
	3. Back-End: System Administration
	4. Back-End: Task Scheduling
	5. Back-End: Static Files
	6. Back-End: Match Code
	7. Interface: Overall
	8. Interface: Viewing/Creating Cases
	9. Interface:  Matches
	10. Interface: Registration
	11. Real Life Administration 
	12. Miscellaneous
=== end ===



=== start TODOs ===

### Section 1 --- Security ###
	
	+ Check whether usage of "if user.is_authenticated and user.is_active:" clause is redundant with the @login_required decorator
	
	++ ONGOING: Use the @login_required decorator everywhere.
	
	++  ONGOING: Make sure that all urls that capture view-function parameters must have extra safety checks
		e.g. if you pass match.id in the url, other users should not be able to access that matchs details 
		by constructing the url. (this is documented better in cases/views.py and matches/views.py

	++ Encrypting the database?

	++ Implement HTTPS/SSL for all pages
		Good reference: https://www.owasp.org/index.php/Main_Page

  	++ Captcha on registration and/or login page?
	 	Maybe not necessary, because automated mass registration of user accounts, doesnt sound like a problem for this site
		Fradulent registration is definitely a problem.

### Section 2 --- Testing ###

	++ Using the test.py functionality within Django to write tests.
		This was not done with tests.py because Zach was still learning Django, he recognizes that he shouldve written a testing suite
		since the beginning and he apologizes for lumping the task on future developers.
		NOTE: I did 'test' everything, in that I made sure models were created and updates appropriately using a manual approach of examining
		the database through the terminal and the admin page.

	++ Create a training or "playground" version for testing with made up data separate from the "live" version.

 	++ Define a data format and create necessary scripts to mass load test data rather than go through system interface?

    ++ Use case reports from Genomics Data journal as training set	

### Section 3 --- Back-End: System Administratior ###
	
	+ Find a way to not have the server username/password in cleartext in settings.py

### Section 4 --- Back-End: Task Scheduling ###

	++ Pick and implement a task-scheduler to schedule match-code execution 
		@WIP: Dave

	+ documents task-schedulers usage in README.md

### Section 5 --- Back-End: Static Files ###

	+ Reorganize static assests into a static_app OR create a global static directory for global assets like Boostrap 3

	+ Double check that the SSIs used in full-tree.html reference files that only contain the JSON HPO information
		This is so that they can be replaced and updated quickly. If a JS variable is left at the beginning of the file,
		a careless copy paste might break it.

### Section 6 --- Back-End: Match Code ###
	
	+ Document match code in README.md or provide a reference to documentation

### Section 7 --- Interface: Overall  ###
	
	++ ONGOING: Use the Django messages framework extensively to confirm the success/failure of any action
		refer to cases/base.html to see how they are rendered

	++ Use named urls in all the templates (replace the old ones)

	+ Big "Contact Us" link on the front page

	++ Tooltips for everything in the application
		There should be no clicking or help search directory.
		Users should be able to hover over a question mark symbol or something similar and a little modal box should popup
		immediately tell them what the thing is for and what information to put in it.
		
	+ Write a 404 error page that isnt ugly
	
	++ Update project to use customized (and most recent) version of Boostrap 3
		Use the color swatch files in the dropbox to customize the color scheme

	+ Public Front Page with Information about GeneYenta
		 When going to the base URL http://geneyenta.cmmt.ubc.ca there should be
    	a 'public' page which just gives a summary of what GeneYenta is etc. From
    	here there should be options to register for the system or login if you
    	are already registered. see the html mockup in the dropbox for ideas.

	++ Style all remaining unstyled pages 
		1. Title Page
		2. All registration pages
		3. Edit a case page

	+ Document HTML/JS in templates
		@WIP: Zach

	+ Display which header tab is currently active
		May need to use JS/JQuery to set the navbar li elements class to active.

### Section 8 --- Interface: Viewing/Creating Cases ####

	+ Replace/improve the validation JS code in edit-case.html
		Use the code from create-cases.html and you may only have to add a hidden alert or similar DOM element.

	++ Investigate safety of using a hidden field to submit JSON phenotype inforamtion

	++ Investigate why there is strange string processing required to decode the JSON Phenotype data

	+ Add a How-To or basic explanation of what information is important for matching so the clinicians spend their time/effort appropriately

	+ Add Privacy Disclaimers and Terms of Use to the application
		They could be placed in two places.
		1. When the user registers for an account.
		2. Each time the user creates a case.

	++ Search Functionality for Matches and Cases
		Allow users to search for a case or a match based on different criteria
		Contact Mike Gottlieb for help with creating JS search code, or look at full-tree.html
		for search code.
	
	++ Implement Archive Message Functionality
		After archiving a patient, give users the ability to write a message that will appear to other users when they receive a match to the archived patient. Will require adding a new textfield/charfield to each patient model and a new view/form that prompts users to enter information.
		This allows users to indicate why the case was solved and tell other users useful information about the condition of said case. 
		e.g. The case was solved and a confirmed diagnosis was documented in a medical paper
		e.g. The condition turned out to be a rare presentation of another disease.
		etc.
	
	+ Maybe each case could have a "View Matches" button to show the matches for
    	that particular case.
    
	++ Can / should a clinician be able to delete a case completely (as opposed
    to just archiving) if for example they enter a case erroneously? Would also
    have to delete all matches for this case.

    + Does the settings view belong here? Maybe there should be a separate
      settings app or a clinician app with a settings view?

### Section 9 --- Interface: Matches ###

	+ Update sorttable_customkey attribute to change when user flags a match as important
		Currently only set once on page load

	++ Search Functionality for Matches and Cases: see same entry under "Interface: Viewing/Creating Cases"

	+ Should the Match Inboxes reference the GeneYenta ID or the Private ID
		As long as they could search by either users said they had no preference, but that was all in theory

	++ Find N More Matches functionality
		Users should have the ability to search for the next N best matches for a given case and display them.
		Daves Notes:
			There probably then needs to be a setting in one of the DB tables
			(cases_patient?) to keep track of how many matches the clinician has
    		previously chosen for each case. Also maybe there should be a "Show Fewer
  		  	Matches" to unclutter the display if finding more matches returns a lot of
 		  	low quality results. "Find More Matches" maybe should be called "Display..."    
			or "Show..." since we are computing all matches but just displaying/showing a select number of them. 

	+ Hide Match Functionality
		Used to hide an undesired match to unclutter the view Matches ui.

	++ Free-Text Analysis of Case Summaries to Facilitate Matching
		A semi-work in progress suggested by Zach, Zach would like to stay involved on this particular TODO
	
	+ Some sort of way to instruct clinicians how to contact each other referencing their match in GeneYenta
		A popup-email client may not be sufficient because users may use all sorts of email clients. 

### Section 10 Interface: Registration ###

	+ Change the signal handler email message in registration.models.py after creating an admin contact email addresss that can send/receive emails.

	+ Make some ModelForm fields unrequired
		Like address2, etc.
		Echo this on the registration template

	+ Checking of username uniqueness
		May be done automatically by Django

	+ Field format checking on registration form
		Can be done with validate.js

	+ Split Name field into Prefix (mr. mrs., etc.), First Name and Last Name

	+ Implement a set of basic robustness requirements for user passwords
		Use validate.js and I would suggest only setting a min. length, instead of char requirements, so as to avoid annoying users

	+ Implement a "Forgot my password" password reset functionality on the home page.

	++ Implement a one-time click link for registration

		After a user submits the initial registration form an email with a one-time click link is sent to their email.
		After clicking it the attribute is_active is set to True.
		This is potentially OK.
		HOWEVER, despite clicking the link, each user needs to be validated by a system admin. Thus, another boolean field needs to be added to the Clinician model that links to the active User model in order to keep track of whether the Clinician is approved. However, this approach needs to have additional conditional checks put in place for each of the views/urls that authenticated users can access. Currently without being approved the user might be able to log into the website. This strategy may require a rewrite of the @login_required (or custom decorator) that checks wether a user is authenticated and active and that the Clinician is approved.

	+ Investigate changing usernames to each users email.
		May cause problems when users move jobs and retire an old email.
		In this instance, it may not be possible to update the username appropriately



### Section 11 --- Real-Life Administration ###

	++ Establish a user approval protocol
		This is less of a coding task, than an administrator task.
		There should be a consistent protocol for approving new users of GeneYenta.

	++ Finish introductory animation
		Natalie Doolittle left behind a series of story boards

	+ Define procedure for checking for and updating HPO tree.


### Section 12 --- Miscellaneous ###

	+ Double-check the current usages of the '|safe' template filter.
		Not sure if used appropriately.

    + Make sure indentation is consistently spaces (no tabs)

    + Add finished GeneYenta website to djangosites.org?

    + Remove debugging print statements from code

    + Turn off DEBUG mode





	





