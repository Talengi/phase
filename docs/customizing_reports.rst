Customizing reports
===================

Phase outgoing transmittals reorts are generated with Reportlab package.
Reports work out of the box but can be completely customized.

Company logo
------------

A company logo can be added on the outgoing transmittals pdf
on a per organisation basis by writing logo settings in a COMPANY_LOGOS dictionnary.

::

    COMPANY_LOGOS = {
        'COMPANY_LOGO_ABC': {'path': abc_logo_path, 'wanted_height': 30, 'x': 13,'y': 40},
        'COMPANY_LOGO_XYZ': {'path': xyz_logo_path, 'wanted_height': 30, 'x': 13, 'y': 40},
    }

where ABC and XYZ are the organisations trigrams.
The logo appears on first page.
This setting must define a path to the logo image file and optionally a wanted_height, logo_x and logo_y in mm.
logo_x and logo_y define logo coordinates
The logo aspect ratio is preserved.


Report templates
----------------

There is no templating mechanism per se, but a simple class defining pdf content and layout.
The base class is transmittals.pdf.BaseTransmittalPdf.
It can be overriden by subclassing it in a module, on a per organisation basis.
Then, each custom pdf generator is referenced in PDF_CONFIGURATION settings
which will provide the dotted path to it.

::

    PDF_CONFIGURATION = {
        'TRANSMITTALS_PDF_GENERATOR_ABC': 'import.path.to.Class_1',
        'TRANSMITTALS_PDF_GENERATOR_XYZ': 'import.path.to.Class_2',
    }

where ABC and XYZ are the organisations trigrams.
