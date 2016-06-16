Django administration
=====================

Superusers can access django admin interface.


Reports
-------

Reports access and appearance in sidebar menu can be controlled by checking
"display report section" in category template.


Contractors and outgoing transmittals
-------------------------------------

Third party users (contractor not belonging to main organisation) can receive a
limited access to Phase in order to
get outgoing tranmsmittals.

First, contractors users have to be created.
The category user relationships must contains a link to the
relevant Outgoing transmittal category.
Then a contractor entity must be created (Contractor Type).
Then, users have to be added to Entity users field.