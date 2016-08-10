# Django example code task
###Install###

1. git clone **https://github.com/AlexeyTernavskiy/django-example-code.git**
2. cd **django-example-code**
3. pip install -r **requirements.txt**
4. bower install
5. python manage.py migrate
6. python manage.py createsuperuser
7. python manage.py loaddata src/apps/product/fixtures/data.json
8. python manage.py test
9. python manage.py runserver --settings=src.core.settings.development
10. open you browser at http://127.0.0.1:8000

####Description:
#####Create django-project with one application in git repositories
-   Add the model `Product` with fields
    -   name
    -   slug
    -   description
    -   price
    -   created\_at
    -   modified\_at
-   Add all the models in the admin panel
    (all of the objects to be displayed on the field name, "view on site" button should work)

-   Create a page with a list of products, to withdraw the name, description and price of the products `(/products/)`

-   Create a product page display name, description, and price of the product `(/products/<product_slug>/)`

-   Add comments on the product page (authorization is not required, the flat, i.e. not tree) page,
    to display the existing comments for the last 24 hours sorted by date of adding (the latest at first)

-   Also on the product page to add the ability to click the `like` product (only for logged users and no more than one time),
    to hold the likes in the database and display the number of likes for each product
    and add the ability to sort by likes at the pages with the list of products

-   To display error forms near the fields

-   Use django.messages for comments and likes

-   Use migrations

-   Follow pep8

-   Write unit tests for the product page with comments

-   Use MySQL or PostgreSQL (at choice)

-   Make two settings available: for development and for deploy

-   All pages should be available on the links

-   Create a generic template and extend from it all the other

-   Add a file with dependencies

-   Optimize the number of requests to database at the pages (cash can be used, but first to reduce the number of unnecessary requests)

-   Basic language - English