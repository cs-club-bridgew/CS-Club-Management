# Invoice Management System

## Programmed by Alex Dasneves

### Installation

To install this program to your server, follow these instructions:

1. Create and source a new Python Virtual Environment
    ```
    python3 -m venv venv
    source ./venv/bin/activate
    python3 -m pip install -r requirements.txt
    ```
1. Initalize the Database

    i. Create a file called db_config.py. Paste the following information, and add in the data from your server:
    ```py
    db_settings = {
        "host": "", # The URI of your database. If the db is on the same machine as the machine running this, use 'localhost'
        "user": "", # The username for the acct to access the db
        "passwd": "", # The password for the acct above
        "db": "invoices" # The database to point to.
    }
    ```
    ii. In your mysql database manager of choice, run the `databaseSetup.sql` file provided. 
    This file will create a primary database called 'invoices', and a backup/test database called 'invoiceTest'

1. Running
    * If you plan on debugging this on a local machine, run
        ```
        flask run --debug
        ```
    * If you wish to deploy this, follow the instructions from DigitalOcean, found [here](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04).

### Usage

#### Running Local

In your MySQL Database Manager of choice, insert a record into the `allowedusers` table in the `Invoices` database.

**If the program is running on your local machine, running flask**
1. Go to localhost:5000/set_user/<record_text>
    
    This will redirect you to the main page after it sets your userID token.

**If the program is running on a non-local machine**
1. Go to <server_uri>/set_user/<record_text>

    This will redirect you to the main page after it sets your userID token.

#### To create a new record, follow these steps

1. Press the 'New Finance Record' button
1. Select an address from the dropdown, or `New Address` for selecting one non in the system
1. Select an appropriate record type. The three choices are:
    * Invoice -- A normal record to track an expense (To be used when total is greater than or equal to $0.00)
    * Credit Invoice -- A record to track a credit to our account (To be used when total is less than $0.00)
    * SGA Budget -- A record to track a credit to our account, granted by the Student Gov't Association
1. Set the appropriate `Record Settings`
    * Record ID is the next ID available to be used, however, any Integer may be provided.
    * Created By should be the person who created the record
    * Approved by should be the officer or external department that approved the request
        * All `Catering Orders` are approved by `University Events`
        * All `SGA Budget Requests` are approved by the `SGA Finance Board` (Cannot be overwritten)
1. Set the appropriate status for the record
    * Open -- Invoice has been approved by the board or external department, and is awaiting payment
    * Paid -- Invoice has been paid out to the external provider, and the goods have not been received.
    * Closed -- Invoice has been paid, and the goods have been received
    * Granted -- The `SGA Finance Board` has approved the request and the funds have been added to our account.
    * Pending -- The invoice is awaiting approval from the board or external department
1. Add all appropriate lines for the invoice
    * Item Description should describe what item was requested
        * SGA Budget Requests lines should depict what was in the budget request
    * Unit Price should show what 1 of that item would cost
    * Quantity should depict how many of that item was purchased
    * Taxes should show how much is to be paid out in tax
    * Fees should show how much is collected in fees by the vendor
    * The total is the calculated 
1. Press `Preview` to verify that all the information is correct. If it is, press the `Create` button.

