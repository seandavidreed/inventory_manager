# INVENTORY MANAGER

#### Video Demo: `<url>`

#### Description:

Years ago, I created a simple inventory ordering spreadsheet for my parents' coffee shop. It had a master list of all inventory items that distributed each item to other sheets in the book according to supplier. These sheets could then be attached to an email and sent to each supplier as an order form. It was a clunky system, but it was a great improvement over the paper system it replaced. The Inventory Manager application was designed to improve upon the spreadsheet design. My aim was to closely resemble the spreadsheet system while streamlining the ordering process and adding two new features: order history and analytics.

For this project, I knew that portability was paramount, so I chose to make a web application. I wanted it to be accessible from any device with a browser. For the Web Application Framework, Flask was my initial choice since I had previous experience with it in CS50x. However, I decided on Django for three main reasons. Django comes with a built-in administrative interface for managing the database, it has a robust user authentication and authorization system, and it has greater security. In a nutshell, Django is a "batteries included" WAF, providing features that would have been very difficult for me to develop without a team behind me.

I knew the data I needed to store in a relational database would be simple, so I chose to work with SQLite3. In models.py, I created three models, Supplier, Item, and Order, that would form tables in the database and store all the web app's data. Entries in the Order table are linked via foreign key to entries in the Item table in a One-to-One relationship, and those in the Item table are linked to those in the Supplier table. These relationships allow the app to generate order forms, order history, and item lists based on the scope required. For example, in the ordering process, I needed to organize the Items according to Supplier so only the items they supply would be submitted to them. [ADD MORE: talk about the components of each model (i.e. send_email BooleanField)]

[VIEWS.PY]

In urls.py, I imported the TemplateView class, which allows templates to be served without a corresponding view. I used this class for all the results templates (e.g. empty-order, delete-occurred, no-data) except success, which needed its own view to handle suppliers with a send_email value of False.

[Explain functions.py]

[Go into static folder]

[Explain structure of templates folder]
