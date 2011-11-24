
European Commission Grants & Commitments Database (FTS)
=======================================================

This is documentation on the process required to generate a valid CSV form of 
the FTS that can be imported into OpenSpending or used for more detailed
analysis.


Loading the XML source files
----------------------------

Download the BUDG source files in the XML format from the Commission's portal 
at http://ec.europa.eu/beneficiaries/fts/index_en.htm. OS doesn't currently 
support multiple languages in data, so you will only want one language version.

Then, load each file into the SQLite staging file::

  python xml2sqlite.py export_20XX_en.xml fts.db


Reconciliation: EC Departments, Countries, Companies
----------------------------------------------------

Recon stages can be run like this::

  python integrate.py cc fts.db
  python integrate.py dg fts.db
  python integrate.py corp fts.db

Companies (corp) reconciliation may potentially take a long time and much user
interaction, so depending on the purpose this may not make sense to reproduce.


EU Budget Reference Data
------------------------

The FTS refers to budget line items in the European budget. These can be used 
to add context to the transaction, by adding in EU budget classifications. 

The required scraper and tools for the EU budget live at: https://github.com/pudo/dpkg-eu-budget

Given that you have loaded the budget CSV into a SQLite database, run the 
following statements::

  CREATE TABLE fts_reference (name TEXT, label TEXT, description TEXT, 
      legal_basis TEXT)
  INSERT INTO fts_reference 
    SELECT DISTINCT title_name AS name, title_label AS label, 
      "" AS description, "" AS legal_baiss FROM budget WHERE volume_name = "Section 3"; 
  INSERT INTO fts_reference 
    SELECT DISTINCT chapter_name AS name, chapter_label 
      AS label, "" AS description, "" AS legal_baiss FROM budget 
      WHERE volume_name = "Section 3"; 
  INSERT INTO fts_reference 
    SELECT DISTINCT article_name AS name, article_label AS label, 
    article_description AS description, article_legal_basis AS legal_basis 
    FROM budget WHERE volume_name = "Section 3";·
  INSERT INTO fts_reference 
    SELECT DISTINCT item_name AS name, item_label AS label, 
    item_description AS description, item_legal_basis AS legal_basis 
    FROM budget WHERE volume_name = "Section 3";·


Contact
-------

* Issues tracker: https://github.com/pudo/dpkg-eu-fts/issues
