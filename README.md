# INVENTORY MANAGER

## Table of Contents:

    1.[Video](# video)
    2. [Description](README.md#description)
        - [models.py](# modelspy)
        - [views.py](# viewspy)
        - [urls.py](# urlspy)
        - [functions.py](# functionspy)
        - [static/](# static)
        - [templates/](# templates)
    3. [Dependencies](# dependencies)
    4. [Testing the App](# testing-the-app)

### Video: `<URL>`

### Description

###### Introduction

Years ago, I created a simple inventory ordering spreadsheet for my parents' coffee shop. It had a master list of all inventory items with each item linked to other sheets in the book according to supplier. These sheets could then be attached to an email and sent to each supplier as an order form. It was a clunky system, but it was a great improvement over the paper system it replaced. The Inventory Manager application was designed to improve upon the spreadsheet design. My aim was to closely resemble the spreadsheet system while streamlining the ordering process and adding two new features: order history and analytics.

For this project, I knew that portability was paramount, so I chose to make a web application. I wanted it to be accessible from any device with a browser. For the Web Application Framework, Flask was my initial choice since I had previous experience with it in CS50x. However, I decided on Django for three main reasons. Django comes with a built-in administrative interface for managing the database, it has a robust user authentication and authorization system, and it has greater security options. In a nutshell, Django is a "batteries included" WAF, providing features that would have been very difficult for me to develop without additional help.

###### models.py

I knew the data I needed to store in a relational database would be simple, so I chose to work with SQLite3. In models.py, I created three models, Supplier, Item, and Order, that would form tables in the database and store all the web app's data. Entries in the Order table are linked via foreign key to entries in the Item table in a One-to-One relationship, and those in the Item table are linked to those in the Supplier table. These relationships allow the app to generate order forms, order history, and item lists based a given scope required. For example, in the ordering process, I needed to organize the Items according to Supplier so only the items they supply would be submitted to them. The Supplier model contains four fields: name, email, send_email, and phone. The app accesses the email field at the end of the take inventory process, sending an order email to each supplier with a send_email value of True. If the value is False, the order form is made available for download as a csv file in the success template. In the Item model, the package and package_qty fields are used together or not at all. They make it possible for an item to be denominated in something larger than one unit. The user can decide what to name the package (e.g. pack, box, case) and how many units it contains; the names themselves do not determine any quantities. Quota is the minimum amount of any given product that must be on hand after restocking has occurred. Storage determines where the unit lives, in the coffee shop  or in the back shed; thus the take inventory list can be separated by storage. Finally, the latest_qty field stores the average order quantity of the last five orders. This value is used to autopopulate the inventory list and help expedite the next ordering process.

###### views.py

In views.py, take_inventory displays all the items in the Item table and allows the user to input the quantity they need to order. The order data is first validated to make sure it isn't all zero values and then stored in the session to be accessed later from the finalize view. By storing the order data in the session, the user is given the option to cancel the order right up until they press the submit order button. In finalize, the user is prompted for an optional message to each supplier before submission. Once they submit, an email with the order attached as a PDF is sent to each supplier where send_email is True.  The user is then directed to the success view. Here, the orders of any suppliers where send_email is False can be downloaded as CSVs.

The views history, archive, and order all go together. The history view displays the latest 20 orders and an archive button that redirects to the archive view, where orders are organized by year for ease of navigation. The order view is accessed by selecting one of the entries in history or archive. The user can see everything that was and was not ordered for that specific order. This is the main purpose of the Order table, to keep an exhaustive record of all units ordered, including both zero and non-zero order quantities.

The final feature, Analytics, allows the user to examine trends in inventory orders. Three data frames are available: Month, Year-to-Date, and All Time. The user can either view the trends of all inventory together or that of a single item. To accomplish all this, I used the Plotly Express module. The default view for analytics is Year-to-Date. If the user selects a different frame (i.e. Month), a post request is sent and the database is queried according to that frame. The data is reformatted and passed into the Plotly Express object, fig. In the final two stages, update_layout is called on fig to further customize the look and feel of the chart and then fig is converted to an HTML string representation.

The last two views, delete and all_data, are accessed from the Django Admin page. The user has the option to "Delete Everything" and to "Download All as CSV". The latter option I was especially keen to include since I didn't want users have their data held hostage should they ever wish to migrate to another inventory management solution.

###### urls.py

In urls.py, I imported Django's TemplateView class, which allows templates to be served without a corresponding view. I used this class for all the results templates (e.g. empty-order, delete-occurred, no-data) except success, which needed its own view to handle suppliers with a send_email value of False. This helped to declutter the views.py file, leaving only the essentials.

###### functions.py

I created the file functions.py to clean up the views.py file. I wrote three functions: createPDF(), createCSV(), and readCSV(). The first of these functions is the most important; it is used to generate the orders that are emailed to suppliers. The second is mainly for the history view; users can download the data of all orders or one order as a CSV file. I included this feature as another way for the user's data to be portable. Finally, readCSV() is a means for the user to upload their data from a CSV file. It's main purpose is to allow the user to upload a spreadsheet they downloaded with the "Download All as CSV" feature. The format generated by the download all feature is the format required for uploading. By separating these functions in their own file, I was able to implement the DRY principle (Don't Repeat Yourself); each function could be used in several different views, and since these uses differed from each other slightly, I used keyword arguments for the functions parameters. That way the function could distinguish the intended use based on the arguments provided.

###### static/

The static folder contains a small styles.css file, images, and scripts.js. In styles.css, I created a custom class selector called login, which is mainly for the purpose of substracting the height of the navbar from the total viewheight. I accomplished this with the calc() function. The JavaScript file contains three functions: increment, check_qty, and toggle_display. The increment function controls the plus and minus buttons in the take-inventory template (the button tag selector in styles.css solves the problem of the screen zooming when the user presses the increment and decrement buttons on a touch screen).

###### templates/

I relied mainly on Bootstrap 5 for the styling of my templates. I wanted Bootstrap's navigation bar and table aesthetics. Since the app is mainly expected to be used on mobile, I needed the navigation bar to be very responsive; Bootstrap has a class, "navbar-collapse", that puts all the navigation links in a dropdown menu once the viewport width reaches a certain breakpoint. Furthermore, Bootstrap's table classes are elegant and simple; considering they make up the whole take-inventory and history templates, the tables needed to be easy to use and clean looking.

### Dependencies

```
pip install django
pip install django-environ
pip install plotly
pip install pandas
```

### Testing the App

```
mkdir inventory_manager
cd inventory_manager

git clone https://github.com/seandavidreed/inventory_manager.git

# install dependencies if you haven't already
pip install django
pip install django-environ
pip install plotly
pip install pandas

# execute command in the same directory as manage.py
# ctrl click http://127.0.0.1:8000/
python3 manage.py runserver

# in the browser, login with these test credentials
# username: root
# password: 12345678*

# navigate to admin in the upper righthand corner
# select users, then root, and update email field to valid address
# select Suppliers and update each email field to valid address

# all set!
```
