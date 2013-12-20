from datetime import date
from random import choice

from django.db import transaction

from documents.models import Document
from categories.models import Category


#DISCIPLINES_CHOICES = [item[0] for item in DISCIPLINES]
#DOCUMENT_TYPES_CHOICES = [item[0] for item in DOCUMENT_TYPES]
#STATUSES_CHOICES = [item[0] for item in STATUSES]
#REVISIONS_CHOICES = [item[0] for item in REVISIONS]
#UNITS_CHOICES = [item[0] for item in UNITS]
#CLASSES_CHOICES = [item[0] for item in CLASSES]
#SEQUENCIAL_NUMBERS_CHOICES = [item[0] for item in SEQUENCIAL_NUMBERS]
#CONTRACT_NBS_CHOICES = [item[0] for item in CONTRACT_NBS]
#ORIGINATORS_CHOICES = [item[0] for item in ORIGINATORS]
#PEOPLE_CHOICES = [item[0] for item in PEOPLE]
#WBS_CHOICES = [item[0] for item in WBS]
#SYSTEM_CHOICES = [item[0] for item in SYSTEMS]
TITLES = (
    "HAZOP report",
    "Cause & Effect Chart - General Shutdown",
    "Unit 000 - CPF BLOCK FLOW DIAGRAM",
    "Liquid Effluent Balance",
    "Chemicals and catalysts consumptions",
    "Solid Waste summary",
    "Gaseous Emissions Balance",
    "Overall Equipment List",
    "CPF Black Start Philosophy",
    "Process Safety Flow Schemes",
    "BASIC ENGINEERING DESIGN DATA  (Project Design Data)",
    "Unit 100 - Receiving Facilities - Material Selection Diagram",
    "Unit 100 - Process Description and Control Philosophy - Receiving facilities ",
    "Cause & Effect Chart - Process Fire Zone PFZ 1 - Units 100, 101 and 102",
    "PID - Unit 100 - Receiving Facilities - Receiving Manifold 1/3",
    "PID - Unit 100 - Receiving Facilities - Receiving Manifold 2/3",
    "PID - Unit 100 - Receiving Facilities - Receiving Manifold 3/3",
    "PID - Unit 100 - Receiving Facilities - Inlet Separators 1/2",
    "PID - Unit 100 - Receiving Facilities - Pig Receiving Area - Part 1",
    "PID - Unit 100 - Receiving Facilities - Pig Receiving Area - Part 2",
    "PID - Unit 100 - Receiving Facilities - Pig Receiving Area - Part 3",
    "PID - Unit 100 - Receiving Facilities - Manifold - Part 1",
    "PID - Unit 100 - Receiving Facilities - Manifold - Part 2",
    "PID - Unit 100 - Receiving Facilities - Manifold - Part 3",
    "Unit 101 - Inlet Booster Compression - Material Selection Diagram",
    "Piping & Instrument Diagram - Unit 101 - Inlet Booster Compression - Gas Inlet Air Cooler",
    "Piping & Instrument Diagram - Unit 101 - Inlet Booster Compression - Inlet Booster Compressor",
    "Piping & Instrument Diagram - Unit 101 - Inlet Booster Compression - Coalescer",
    "Unit 102 - H2S & Mercury Removal - Material Selection Diagram",
    "Piping & Instrument Diagram - Unit 102- H2S & HG Removal - Mercury Guard Bed",
    "Piping & Instrument Diagram - Unit 102- H2S & HG Removal - H2S Removal Vessel 1/2",
    "Piping & Instrument Diagram - Unit 102- H2S & HG Removal - H2S Removal Vessel 2/2",
    "Cause & Effect Chart - Process Fire Zone PFZ 2 - Units 103, 107 and 306",
    "Unit 103 - Amine Unit - Process Flow Diagram",
    "Piping & Instrument Diagram - Unit 103 - C02 Removal Interface",
    "Unit 104 - Gas Dehydration - Material Selection Diagram",
    "Cause & Effect Chart - Process Fire Zone PFZ 3 - Units 104, 105, 106, 301 and 304",
    "THERMAL OXIDATION PACKAGE - 104-UY-100  - DUTY SPECIFICATION - ",
    "Unit 104 - Thermal Oxydation - Process Flow Diagram",
    "Piping & Instrument Diagram - Unit 104 - Gas Dehydration - Wet gas Coalescer",
    "Piping & Instrument Diagram - Unit 104 - Gas Dehydration - Glycol Contactor",
    "Piping & Instrument Diagram - Unit 104 - Gas Dehydration - Dehydrated Gas Coalescer",
    "Piping & Instrument Diagram - Unit 104 - Gas Dehydration - Glycol Regeneration Package 1/3",
    "Piping & Instrument Diagram - Unit 104 - Gas Dehydration - Glycol Regeneration Package 2/3",
    "Piping & Instrument Diagram - Unit 104 - Gas Dehydration - Glycol Drain Sump",
    "Piping & Instrument Diagram - Unit 104 - Gas Dehydration - Thermal Oxydation Package",
    "Unit 105 - Gas Dew Pointing - Material Selection Diagram",
    "Piping & Instrument Diagram - Unit 105 - Gas Dew Pointing - Cold Box",
    "Piping & Instrument Diagram - Unit 105 - Gas Dew Pointing - Cold Separator and Expander KO Drum",
    "Piping & Instrument Diagram - Unit 105 - Gas Dew Pointing - Turbo Expander",
    "Piping & Instrument Diagram - Unit 105 - Gas Dew Pointing - Recompressor",
    "Unit 106 - Condensate Stabilisation - Material Selection Diagram",
    "Heat Exchanger Process Data  Sheet -  Stabiliser Reboiler (106-GA-014)",
    "PUMP PROCESS DATASHEET  CONDENSATE RECYCLE PUMP 106-PA-022",
    "Piping & Instrument Diagram - Unit 106 - Condensate Stabilisation - Condensate Pre-Heating",
    "Piping & Instrument Diagram - Unit 106 - Condensate Stabilisation - Condensate Flash Drum",
    "Piping & Instrument Diagram - Unit 106 - Condensate Stabilisation - Stabilisation Column",
    "Piping & Instrument Diagram - Unit 106 - Condensate Stabilisation - Condensate Degassing Drum",
    "Piping & Instrument Diagram - Unit 106 - Condensate Stabilisation - Off Gas Compressor 1/2 - Train A",
    "Piping & Instrument Diagram - Unit 106 - Condensate Stabilisation - Off Gas Compressor 2/2 - Train A",
    "Piping & Instrument Diagram - Unit 106 - Condensate Stabilisation - Off Gas Compressor 1/2 - Train B",
    "Piping & Instrument Diagram - Unit 106 - Condensate Stabilisation - Off Gas Compressor 2/2 - Train B",
    "Piping & Instrument Diagram - Unit 106 - Condensate Stabilisation - Column Reboilers ",
    "Unit 200 -  Gas Metering & Export  - Material Selection Diagram",
    "Cause & Effect Chart - Process Fire Zone PFZ 8 - Unit 200 and Unit 100 inlet manifold",
    "PID - Unit 200 - Gas Metering & Export - Fiscal Metering Packages",
    "Piping & Instrument Diagram - Unit 200 - Gas Metering & Export - Block Valves",
    "Piping & Instrument Diagram - Unit 200 - Gas Metering & Export Pig Launcher",
    "UNIT 200-GAS EXPORT PIPELINE PIG RECEIVER-TIE IN TO GR5",
    "Cause & Effect Chart - Fire Zone FZ 10- Units 201 and 309",
    "Piping & Instrument Diagram - Unit 201 - Condensate Metering, Storage & Export - Condensate Storage Tank",
    "Piping & Instrument Diagram - Unit 201 - Condensate Metering, Storage & Export - OffSpec Storage Tank",
    "Piping & Instrument Diagram - Unit 201 - Condensate Metering, Storage & Export - Condensate Drain Drum",
    "Unit 300 - Power Generation & Waste Heat Recovery - Material Selection Diagram",
    "Cause & Effect Chart - Miscellaneous Fire Zone MFZ 13 - Unit 300",
    "PID - Unit 300 - Main Power Generation & WHRU - Gas Turbine & WHRU - Train 1",
    "PID - Unit 300 - Main Power Generation & WHRU - LP Fuel Gas Supply - Train 1",
    "PID - Unit 300 - Main Power Generation & WHRU - Gas Turbine & WHRU - Train 2",
    "PID - Unit 300 - Main Power Generation & WHRU - LP Fuel Gas Supply - Train 2",
    "PID - Unit 300 - Main Power Generation & WHRU - Gas Turbine & WHRU - Train 3",
    "PID - Unit 300 - Main Power Generation & WHRU - LP Fuel Gas Supply - Train 3",
    "Unit 301 - Hot Oil - Material Selection Diagram",
    "VESSEL PROCESS DATA SHEET HOT OIL EXPANSION VESSEL 301 - VL - 001",
    "PUMP PROCESS DATASHEET HT HOT OIL RECIRCULATION PUMPS 301 - PA - 002 A/B",
    "Air Cooler Process Data Sheet - LT Hot Oil Trim Cooler - 301 - GC - 013",
    "PID - Unit 301 - Hot Oil distribution loop - Hot Oil storage & drain",
    "PID - Unit 301 - Hot Oil - High Temperature Distribution ",
    "PID - Unit 301 - Hot Oil - High Temperature Recirculation",
    "PID - Unit 301 - Hot Oil - Storage Tank",
    "PID - Unit 301 - Hot Oil - Drain Drum",
    "PID - Unit 301 - Hot Oil - HT Hot Oil Distribution",
    "Cause & Effect Chart - Fire Zone FZ 11 - Units 302, 303, 308, 400, 401, 402 and 403",
    "Vessel (Vertical) Process Data Sheet - Instrument Air Receiver - 302-VL-004- ",
    "Unit 304 - Fuel Gas Network - Material Selection Diagram",
    "Piping & Instrument Diagram - Unit 304 - Fuel Gas System - HP Fuel Gas Drum",
    "Piping & Instrument Diagram - Unit 304 - Fuel Gas System - LP FUEL GAS DRUM 1",
    "Piping & Instrument Diagram - Unit 304 - Fuel Gas System -LP FUEL GAS DRUM 2 & 3",
    "Piping & Instrument Diagram - Unit 304 - Fuel Gas System - LP & HP Fuel Gas Distribution",
    "Cause & Effect Chart - Process Fire Zone PFZ 9",
    "305-UF-001 HP Flare Package - Duty Specification",
    "Pump Process Data Sheet - HP Flare KO Drum Pumps 305-PA-017 A/B",
)


#@transaction.commit_on_success
#def generate_random_documents(nb_of_docs, categories=None):
#    """Generate a bunch of random documents.
#
#    This function is useful for testing purpose.
#
#    """
#    if not categories:
#        categories = list(Category.objects.all())
#
#    for i in range(nb_of_docs):
#        max_revision = choice(range(1, 5))
#        document = Document.objects.create(
#            title=choice(TITLES),
#            status=choice(STATUSES_CHOICES),
#            unit=choice(UNITS_CHOICES),
#            discipline=choice(DISCIPLINES_CHOICES),
#            document_type=choice(DOCUMENT_TYPES_CHOICES),
#            system=choice(SYSTEM_CHOICES),
#            klass=choice(CLASSES_CHOICES),
#            leader=choice(PEOPLE_CHOICES),
#            approver=choice(PEOPLE_CHOICES),
#            contract_number=choice(CONTRACT_NBS_CHOICES),
#            originator=choice(ORIGINATORS_CHOICES),
#            sequencial_number=choice(SEQUENCIAL_NUMBERS_CHOICES),
#            wbs=choice(WBS_CHOICES),
#            created_on=date.today(),
#            current_revision=u"{0:0>2}".format(max_revision),
#            current_revision_date='{year}-{month:0>2}-{day:0>2}'.format(
#                year=2008 + max_revision,
#                month=choice(range(1, 13)),
#                day=choice(range(1, 29)),
#            ),
#        )
#        for revision_number in range(max_revision):
#            DocumentRevision.objects.create(
#                revision=u"{0:0>2}".format(revision_number),
#                revision_date='{year}-{month:0>2}-{day:0>2}'.format(
#                    year=2008 + revision_number,
#                    month=choice(range(1, 13)),
#                    day=choice(range(1, 29)),
#                ),
#                document=document,
#            )
#
#        category = choice(categories)
#        category.documents.add(document)
#        category.save()
