# Preyes-Backend

## Table of contents
1. [Description](#description)
   1. [Application function](#application-function)
   1. [Technology choices](#technology-decisions)
   2. [Problems faced during development & Future features](#problems-and-future-features)
2. [Installation](#installation)
3. [Endpoints](#endpoints)
   1. [Customer](#customer-endpoint)
   2. [Customer-details](#customer-details-endpoint)
   3. [Forgot-password](#forgot-password)    
   4. [Reset-password](#reset-password) 
   5. [Login](#login)
   6. [Logout](#logout)
   7. [Product-items](#product-items)
   8. [Product-items-details](#product-items-details)
   9. [Product-items-category](#product-items-category)
   10. [Categories](#categories)
   11. [Categories-details](#categories-details)
   12. [Targetlist](#targetlist)
   13. [Targetlist-crud](#targetlist-crud)
   14. [Device-register](#device-register)
5. [Credits](#credits)
6. [Sources](#sources)
7. [License](#license)

## Description <a name="description" />
### What our application does <a name="application-function" />
The name for our is Preyes, this name is a play of words. The name is based on the combination of prices and eyes, because our application is based around monitoring prices of products. The name can also be read with a negative connotation, but with the logo we hope to steer away from this negative connotation.

For people who want to buy products from websites, but find these products too expensive to buy at the current price, we Preyes provide the possibility to notify you when a product reaches a certain price point you want. Our product differs from other product trackers by providing a single place to track wanted items and is usable on the go as an app.

Our first version of the app will focus solely on the retailer Bol.com, but in the future we will add new retailers to our catalogue of products. Other retailers we might add in the future are Coolblue and Amazon, because these retailers are also big online retailers in the Dutch webshop market.

### Technology decisions <a name="technology-decisions" />
Technology decisions: Django, Postgresql, Heroku  
**Arguments:**
* The documentation for Django is good because it covers a lot of topics. Because of the broad documentation that is available we can implement functionalities that Django offers better (Daftari, 2020).
* Django also runs on python in which we have experience in. This gives us a headstart in programming, whereas programming in an unfamiliar language might cost some time which can possibly hinder our project.
* Django is great for building API’s because of its REST framework(Daftari, 2020). By using the REST framework to build APIs we can easily expose data to our endpoints
* Our team wants to use Postgresql primarily for the fact that relations can be defined between tables. In our project, our data will need to have relationships in order for our functionalities to work efficiently. 
* We want to use Heroku, since Heroku is the cheapest solution for our application.
Heroku is not suitable for high traffic, but it has the ability to upscale.(Django Stars, 2020). We also have previous experience with deploying personal projects on Heroku.


### Problems faced during development & Future features <a name="problems-and-future-features" />
Because we mostly work with external API's, we had to be resourceful with the request limitations. Also every API has its own structure when returning the products from an request, so we had to make a data structure that would be generic enough to fit every retailer.
We currently only support one retailer, but in the future we hope to integrate more retailers into our application.
The application currently is only for Android, but we would like to be able to make the application available for IOS and Android.


## Installation <a name="installation" />



## Endpoints <a name="endpoints" />

For the endpoints we use the following base url

preyesserver.herokuapp.com

With this base url the following paths are used as endpoint for requests

### Customer <a name="customer-endpoint" />
url: preyesserver.herokuapp.com/customers/

#### GET request
Params: None
This endpoint returns all customers if the person who requests this has a session key. An session key can be obtained by login in first.

#### POST request
Params: username(string), password(string), email (string), first_name(string), last_name(string)
By giving the following params to the endpoint, an user will be created for the app

### Customer details <a name="customer-details-endpoint"/>
url: preyesserver.herokuapp.com/<int:pk>/

#### GET request
Params: pk(int)
Returnsdetails of a customer based on pk

#### PUT request
Params: pk(int), Optional username(string), password(string), email (string), first_name(string), last_name(string)
To change the fields of a user you can give some optional fields alongside the pk to perform changes.

#### DELETE request
Params: pk(int)
This endpoint deletes a customer with the given pk

### Forgot password <a name="forgot-password"/>
url: preyesserver.herokuapp.com/forgot_password/

#### POST request
Params: email(string)
With this endpoint user's get send an email in which they get redirected to  reset their password. 

### Reset password  <a name="reset-password"/>
url: preyesserver.herokuapp.com/reset_password/

#### POST request
Params: GUID(string), password(string)
With this endpoint user's can create a new password based on the GUID if that value is valid

### Login <a name="login"/>
url: preyesserver.herokuapp.com/login/

#### POST request
Params: username (string), password(string)
With this endpoint a registered user can login to his/her account by giving their username and password

### Logout <a name="logout"/>
url: preyesserver.herokuapp.com/logout/

#### POST request
Params: None
With this endpoint an user is logged out based on his given session key

### Product_items <a name="product-items"/>
url: preyesserver.herokuapp.com/product_items/

#### GET request
Params: None
Returns all product_items if the session key is valid

### Product_items details  <a name="product-items-details"/>
url: preyesserver.herokuapp.com/product_items/<int:pk>/

#### GET request
Params: pk(int)
Returns the details of a product_item based on primary key

#### PUT request
Params: pk(int), optional name(string), description(string), specs_tag(string), product_url(string), image_url(string), price(double), old_price(double), last_updated_at(datetime), in_stock(boolean)
With this endpoint you can change the values of the given optional params

#### DELETE request
Params: pk(int)
Deletes a product_item based on pk

### Product_items based on category <a name="product-items-category"/>
url: preyesserver.herokuapp.com/product_items/category/

#### GET request
Params: in url -> customer_id(int), categories(string)
Returns product items based on preferred categories of a user or a specific category given in the url

### categories <a name="categories"/>
url: preyesserver.herokuapp.com/categories/

#### GET request
Params:None
Returns all categories if session is valid

### category details <a name="categories-details"/>
url: preyesserver.herokuapp.com/categories/<int:pk>/

#### GET request
Params: pk(int)
Returns category based on pk if session is valid

#### PUT request
Params: pk(int), name(string), retailer_id(foreign key Retailer)
Updates the name and retailer_id of the category

#### DELETE request
Params: pk(int)
Deletes category with the given pk

### Targetlist of user <a name="targetlist"/>
url: preyesserver.herokuapp.com/targetlist/<str:email>/<int:pk>/

#### GET request
Params: email(string),pk(int)
Returns targetlist of a user based on his email and his target_item if the pk of a product_item is given

#### POST request
Params: email(string),pk(int), target_price(double)
Updates the target_price of a target_item in a users targetlist

### crud on target_itemns in Targetlist of user <a name="targetlist-crud"/>
url: preyesserver.herokuapp.com/targetlist/<str:email>/

#### GET request
Params: email(string)
Returns all target_items in the target_list of a user

#### POST request
Params: email(string), target_price(double), product_item_reference_id(int),target_type(string)
Creates a new target_item with a target_price and target_type for a user in his target_list

#### PUT request
Params: email(string), target_price(double), product_item_reference_id(int),target_type(string)
Updates the target_price or target_type of a  target_item for a user in his target_list

#### PUT request
Params: email(string), product_item_reference_id(int)
Deletes a target_item for a user in his target_list based on the product_item_reference_id

#### POST request
Params: email(string),pk(int), target_price(double)
Updates the target_price of a target_item in a users targetlist


### Device/register <a name="device-register"/>
url: preyesserver.herokuapp.com/device/register/

#### POST request
Params: registration_id(int), id
creates and registers a new device for the user based on his own id and registration_id for his device

## Credits <a name="credits" />
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->

[![All Contributors](https://img.shields.io/badge/all_contributors-3-orange.svg?style=flat-square)](#contributors-)

<!-- ALL-CONTRIBUTORS-BADGE:END -->

## Sources <a name="sources" />
* Daftari, S. (2020, 30 april). Top 10 Pros of using Django framework for back-end web development. 10 Reasons Why Django Web Development with Python is Most Popular for Backend Web Development. https://www.kelltontech.com/kellton-tech-blog/why-django-web-development-with-python-for-backend-web-development
* Django Stars. (2020, 6 november). Top 6 Django Compatible Hosting Services. Django Stars Blog. https://djangostars.com/blog/top-django-compatible-hosting-services/


## License <a name="license" />
