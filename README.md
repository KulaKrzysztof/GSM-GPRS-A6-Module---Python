# GSM GPRS A6 Module - Python Script
Control GSM modem using Python Script - Apache will run page with form (phone number and content will save in db) and the same python script run in background will send SMS messages.

### Running

This script consists of:
* python script (index.py),
* file of sqlite3 datatabase, 
* htaccess file,
* text file with key (token) to HTML form,

This script is checking which user ran their. If this script will by execute by apache (www-data user) -> return will be of html form. After completed the form, data will save in sqlite3 database. If you run script by other user - will be established connection with sqlite3 database. Now with 30 seconds timeout will be downloaded messages from database and will send. 