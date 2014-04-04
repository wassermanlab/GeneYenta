		README.md	GeneYenta	Aug. 30, 2013
		
			by Zach Maurer

		=== Contents ====
		1. Overview of the application
		2. Discussion of Each Django App's Functions
		3. Overview of the front-end application
		4. Overview of data submission procedures
		5. Overview of external software APIs used
		6. @TODO: Overview of task scheduling
		7. Helpful Links for Strange Problems
		8. Developers' Contact Information 
		=== end Contents ===

// To jump to a chapter search "Section [section number]"


### Section 1 -- Overview of the application ###

GeneYenta is an online case-matching tool that runs off Django, a python-based, open source framework (see https://www.djangoproject.com/). Django is actively maintained and there is a strong user community the two primary resources are the official documentation and the StackOverflow website.
		
Although the documentation for Django is quite thorough, I will provide a brief introductionto the API's structure:

+ A Django project is composed of multiple different "apps"

A single project (i.e. GeneYenta) is composed of multiple applications (Cases, Registration, Matches). These applications are not "apps" in the common-sense. They are instead ways of organizing code based on functionality to the end-user or otherwise. One could write a whole Django website with only one app (there is no limit to the amount of code/functionality in each app), but it would become very confusing and spaghetti-like. 

NOTE: When you starts a project through the "startproject" command-line action, you will create a root project folder. This is distinct from an "app" because it only contains the information required to configure and weave together the other applications. It should not have a models.py, template files or static files.  

+ Each app is separated into 3 parts: Models, Views and Templates.
		
1. The Models are essentially a python-class/Django representation of the database tables.There are many provided options for model fields provided by Django (equivalently the database table) and if one desires there is plenty of room to customize the functionality.The './manage.py syncdb' commands, './manage.py dbshell' and other command-line functionality provide the easiest ways of interfacing with the database. 

NOTE: Some of the inidivudal Model fields attributes (expressed as kwarg parameters) are not translated directly to MySQL. Some of the attributes like 'models.BooleanField(default=False)' are not set to have a default value in the the actual MySQL table.

2. The Views are the python functions that are called to (1) retrieve records from the database (2) manipulate/filter/modify the data and (3) prepare the data
for presentation in the templates. There are some built-in/contributed views provided by Django. One example is the authentication package, which takes care of the logic around authenticating and registering user accounts.  The view functions are called whenever a user visits a particular url.

=== A Brief Note on Urls ===
URLs are the means through which an app's functionality is called into use. It starts in the urls.py file in the root-folder. This is known as the URL-conf. When a user tries to visit a certain url, a portion of it will be evaluated by the URL-conf. Then based on the regular expression matches found in that file, Django will pass the remainder of the url to the appropriate urls.py file in the appropriate application. Then, another set of regex's are matched to by the application. If a match is found, the url function will call a view function. In this way, the urls are the "glue" between the user's urls visitations and calling up a page. This was a brief description and the process is well explained in the Django docs (https://docs.djangoproject.com/en/dev/topics/http/urls/).
=== end ===

So, the view functions are called based on when a user visits a url. When data is retrieved from the database, everything is converted into a python object and can be manipulated as such. 

NOTE: Django db queries will return proprietary Django objects in some instances, that may behave slightly differently than the models. Again, this behavior is well documented under areas like "QuerySet" and "QueryDict" of the Django docs.

Finally, the views render templates by creating a context dictionary that is passed to the templates. This context dictionary is a mapping of python variables found in the scope of the view function being called to strings. These strings become the variable names that are accessed in the templates via the templating language (simplified python).

3. The templates control the the frontend presentation of data passed to it by the views functions. The Django templating language and system is well-designed and allows developers to dynamically extend base templates (or templates of template files) to reduce code duplication. (Such as the case where the nav bar in GeneYenta shows up on each and every page, but it is only included once in the cases/base.html)

=== A Brief Note on FK's and Related Object Lookups ===
	Read this documentation: https://docs.djangoproject.com/en/dev/topics/db/queries/
	Specifically, read this section on Related Objects (shows how to trace a Foreign Key backwards, used to link User and Clinician objects):
		https://docs.djangoproject.com/en/dev/topics/db/queries/#related-objects
=== end ===


### Section 2 -- Discussion of Each Django App's Functions ###

Registration
	"Registration" provides all the necessary functionality to register new users and communicate the status/success of their registration process. Also, this application contains the initial redirect function that will redirect authenticated users to their "View Matches" page and unauthenticated users to the login screen. The login functionality is covered by a contributed Django view (built-in and documented). This application contains some of the heaviest usage of contributed Django views, because the authentication process is provided by Django and well-doc'd. If you cannot find a view function in views.py that takes care of some specific functionality, look in urls.py to make sure that a contributed core view function is not being called.

Cases
	"Cases" encapsulates all the logic and templates required to archive patients-cases, view/create/edit patients-cases and change a users's personal settings or information. This is the largest app, and basically all the webpages that authenticated viewers can access extend the "cases/base.html" file. 

The tree-selector and HPO JSON data are contained in the static directory of this app.

Matches
	"Matches" takes care of the code required to retrieve and display all matches for every patient and view the details of a given match. 

=== A Note on Static Files ===
Each app can have static files. However, at the time of writing this readme, most of the pertinent static files were kept in cases/static.
In the future there should be a new application whose only function is to have a static folder with alls the apps static files in one place.
for example,
	--/static_app <-- (root app directory)
		|- ...
		|- static
			|- static_app <--- (the name spacing requirement for Django folder finders)
				|- cases <-- (added subdirs for each app)
					|- js
					|- css
					|- etc...
				|- matches
					|- other stuff, like above
				|- registration
					|- stuff
				|- global <--- (potentially having a global static file dir for global assets like the bootstrap3 markup)

		|- media <--- (the above dir structure could be repeated for the media assets)
			|- ...
=== end ===


### Section 3 -- Overview of Application's Frontend ###

+ JQuery
	JQuery is used for multiple things in GeneYenta. The JQuery plugins used will be convered in Section 5 and JQuery's role in client-side data submission of phenotype info is convered in Section 5.

NOTE: It may be wise to use Google's CDN for jquery, because it provides the potential to relieve strain on our server, provide faster localized downloads and potentially take advantage of client-side caching.

+ Bootstrap 3 -- Main CSS and JS

GeneYenta uses Twitter's Bootstrap 3 (http://getbootstrap.com/) as its front-end framework, primarily. This framework is awesome. It provides a responsive grid system that scales very well on mobile and tablet devices. Also, it makes organizing html on the page a breeze. At times, you have to be a little vigliant with using the grid markup (most of the css is applied via class html-attributes) because if you don't plan ahead and don't make strategic use of embedded grids/columns, you may end up having a lot of extra div's floating around clogging up the semantic value of the html.

Be sure to make intelligent and consistent use of all the different column sizes and be aware of what the site looks like when you contract or expand the window.

+ Django Messages -- Alerts Notifying Users of Successful/Unsuccesful Actions
Django provides an internal messaging/alert framework for displaying messages to users. These messages are created in the views functions and displayed via the template code in cases/base.html. 

NOTE: The extra_tags kwarg in messages.add_message is used to set the appropriate alert class markup from Bootstrap 3.

Read more on the django messaging framework at the official docs (https://docs.djangoproject.com/en/dev/ref/contrib/messages/).


### Section 4 -- Overview of Data Submission Procedures ###


To understand the data subumission process it is necessary to understand the uses of the request object and the subtleties of 'cleaning' data.

+ Most of the data submission is done via traditional html form elements and back-end processing within a views function.

At the moment most of the major formsets are created via Django's ModelForm subclasses which automatically create a series on inputs and forms based on the Model's fields. These are displayed in the templates and processed in the views. 

	In general submitting a form follows this idiom:
		
		def foo(request):
    		if request.method == 'POST': # If the form has been submitted...
        		form = ContactForm(request.POST) # A form bound to the POST data
        			if form.is_valid(): # All validation rules pass
            			# Process the data in form.cleaned_data
            			# ...
            			return HttpResponseRedirect('/thanks/') # possible redirect after POST
   			else:
        		form = ContactForm() # An unbound form
			return render(request, 'contact.html', {
					'form': form,
    			})
	Found @ https://docs.djangoproject.com/en/dev/topics/forms/#using-a-form-in-a-view


+ AJAX

Some of the UI components require the use of asychronous submissions. One working example, are the "Important" checkboxes/markers on each of the match notification. When users click this checkbox a small amount information is passed to a view via JQuery's JQuery.ajax() (http://api.jquery.com/jQuery.ajax/) without refreshing the page. This is processed by a function that uses the conditional method, is_ajax(). The documentation on this is here https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpRequest.is_ajax. 

There is also a useful directory covering all sorts of packages/discussion for Django/AJAX: https://code.djangoproject.com/wiki/AJAX.



### Section 5 -- Overview of External API's Used ###


+ Django Extensions

Docs: http://pythonhosted.org/django-extensions/shell_plus.html
Docs: http://pythonhosted.org/django-extensions/index.html 

NOTE: Not sure if the following URL for django-extensions is just the GitHub repo of the same project or a completely different project
Docs??: https://github.com/django-extensions/django-extensions

Django extensions was mostly for it's shell_plus command-line utility which auto imports all your models. Make testing in the command-line much faster.  


+ validate.js

Docs: http://rickharrison.github.io/validate.js/

Awesome front-end validation API that makes it very easy to validate the input in a form field based on a set of specific and useful rules BEFORE the page sends any data.

Very useful for stopping Django 404s or page refreshes and vague missing field error messages provided by Django. Also, very important on the create/edit case pages because, if the page refreshes and submits incomplete data, the phenotype information selected via JQuery/JS will be lost and the user will be very angry.

+ sorttable.js

Docs: http://www.kryogenix.org/code/browser/sorttable/

Allows tables to be sortable via clicking on the headers. Use the sorttable_customkey attribute if problems arise (very helpful documentation).


+ popup.js

Docs: http://www.nicolashoening.de/?twocents&nr=8

NOTE: not to be confused with http://docs.toddish.co.uk/popup/ (although this seems useful too)

This is used for creating hover-popups and is used when viewing match notes.

+ Bootstrap 3

Docs: http://getbootstrap.com/ 
Front end frame work with a lot of customizeable peices. Needs JQuery to run.


+ JQuery

Docs: http://jquery.com/
JS DOM manipulation library.


+ Dynatree

@TODO
Contact Mike Gottlieb.

Used for navigating the HPO.


### Section 6 -- Overview of Task Scheduling ###

A task scheduler will be needed to run the match.py code whenever it is appropriate.

Dave A. is looking into that now:
Celery has been proposed to handle this task. Another (simpler?) possibility is to simply have a table with a single record in the DB with a match update flag field and possibly some date and match type (all patients or single patient match) fields. The matching program will check if this flag is set and if not, set the flag and proceed with the matching. When the matching is complete, the match program will clear the flag (and update the data fields with the start/end date/time of the matching process). If this is done the match program will have to have some sort of retry loop and time out after some period if the flag remains set. In this case an e-mail notification will need to be sent to the GY administrator to inform them of a possible problem (the last match process failed to finish and did not clear the flag). This may get more complicated in which case Celery might be the way to go.

@TODO: write docs


### Section 7 -- Helpful Links (for Strange Problems or Otherwise) ###


A deprecated approach to creating a Profile. No need to mess with AUTH_PROFILE_MODULE
http://stackoverflow.com/questions/6085025/django-user-profile

Sending emails on user activation using a Signal Handler
http://stackoverflow.com/questions/3441725/sending-emails-when-a-user-is-activated-in-the-django-admin

HTTPS and SSL with Django
http://security.stackexchange.com/questions/8964/trying-to-make-a-django-based-site-use-https-only-not-sure-if-its-secure

Testing with Django
http://toastdriven.com/blog/2011/apr/10/guide-to-testing-in-django/

Django's defence again XSS and Basic Web Attacks 
http://security.stackexchange.com/questions/27805/is-djangos-built-in-security-enough

Possible way of handling on demand encrpyting/decrypting db info
http://stackoverflow.com/questions/13077109/how-can-i-create-an-encrypted-django-field-that-converts-data-when-its-retrieve

A guide to serving static files with Django
http://dlo.me/archives/2013/01/14/how-to-serve-static-files-django/

Accessing dictionary elements in Django templates
http://stackoverflow.com/questions/1275735/how-to-access-dictionary-element-in-django-template

Subtle bug with JQuery.ajax() URL parameter
http://stackoverflow.com/questions/13731880/django-ajax-unable-to-get-ajax-post-data-in-the-views-py

Turning a checkbox into something else visually
http://stackoverflow.com/questions/8667528/custom-pictures-for-checkbox

Sans Serif Fonts
http://piefoundry.com/10-of-the-best-sans-serif-fonts/

A directory (not sure if complete) of Django E-Commerce Packages
https://www.djangopackages.com/grids/g/ecommerce/

Why using Google's CDN may be good
http://encosia.com/3-reasons-why-you-should-let-google-host-jquery-for-you/


### Section 8 --- Developer's Contact Information ###

Zach Maurer -- Worked on the project full-time from Jul. 2013 - Sept. 2013
Email1: zach.maurer@gmail.com
Email2: zmaurer@stanford.edu
Skype: zach.daniel.maurer

David Arenillas -- Working on project since Jul. 2013
Email: dave@cmmt.ubc.ca

@TODO: Fill in other contact info's


=== end docs // see TODO.md for a list of project deficiencies or overall tasks to accomplish ===


