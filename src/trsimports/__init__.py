"""This is the transmittals import feature.

The purpose of this feature is to let a contractor (ctr) push documents
to the client's phase installation.

To do this, the contractor must upload a directory (e.g through a ftp
server) containing the following files:

  * a csv file containing the list of documents and their metadata.
  * for each line in the csv, the actual document as a pdf and, optionnaly, a
    native file.

The import steps are run in this order:

  1) automaticaly checks that the uploaded directory is correct
    * check naming conventions
    * check csv syntax
    * check data validity
    * check correct file presence
    * etc.
  2) warn the document controller that a transmittals sheet is ready to be reviewed
  3) upon DC's validation, create the documents in Phase

"""
