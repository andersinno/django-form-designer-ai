Django Form Designer (AI Fork)
******************************

Unmaintained
============

This fork is unmaintained.  There's an alternative fork at
https://github.com/kcsry/django-form-designer

Acknowledgements
================

This project is a fork of https://github.com/samluescher/django-form-designer .
Thanks, @samluescher!

This fork is compatible with Django 4+ and Python 3.7+.

General
=======

A Django admin app with a GUI to create complex forms without any programming skills;
complete with logging, validation, and redirects.

**Key features**:

* Design contact forms, search forms etc from the Django admin, without writing any code
* Form data can be logged and CSV-exported, sent via e-mail, or forwarded to any web address
* Use drag & drop to change the position of your form fields
* Fully collapsible admin interface for better overview over your form
* Implements many form fields included with Django (TextField, EmailField, DateField etc)
* Validation rules as supplied by Django are fully configurable (maximum length, regular
  expression etc)
* Customizable messages and labels
* Supports POST and GET forms
* Signals on form render, submission, success, error.
* Supports google reCAPTCHA service


Basic setup
===========

- Add ``form_designer`` to your ``INSTALLED_APPS`` setting::

        INSTALLED_APPS = (
            ...
            'form_designer',
        )

- For basic usage, add URLs to your URL conf. For instance, in order to make a form named
  ``example-form`` available under ``http://domain.com/forms/example-form``,
  add the following line to your project's ``urls.py``::

    urlpatterns = patterns('',
        (r'^forms/', include('form_designer.urls')),
        ...
    )


Optional requirements
=====================

The form_designer admin interface requires jQuery and the jQuery UI Sortable
plugin to make building forms a lot more user-friendly. The two Javascript
files are bundled with form_designer. If you want to use you own jquery.js
instead because you're already including it anyway, define JQUERY\_JS in your
settings file. For instance::

    JQUERY_JS = 'jquery/jquery-latest.js'

Running tests
=============

Use `tox`.
