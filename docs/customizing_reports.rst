Customizing reports
===================

Phase outgoing transmittals reorts are generated with Reportlab package.
Reports work out of the box but can be completely customized.

Company logo
------------

A company logo can be added on the outgoing transmittals pdf
on a per organisation basis by writing logo settings on this pattern: COMPANY_LOGO_XXX where XXX is the organisation trigram.
The logo appears on first page.
This setting is a dict and must define a path to the logo image file and optionally a wanted_height, logo_x and logo_y in mm.
logo_x and logo_y define logo coordinates
The logo aspect ratio is preserved.


Report templates
----------------

There is no templating mechanisme per se, but simple class defining pdf content and layout.
The base class is transmittals.pdf.BaseTransmittalPdf.
It can be overriden by subclassing it in a module, on a per organisation basis.
Then, this custom pdf generator is referenced in TRANSMITTALS_PDF_GENERATOR_XXX settings
which will provide the dotted path to it, where XXX is the organisation trigramm defined in db.