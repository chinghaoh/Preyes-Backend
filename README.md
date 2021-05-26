# Preyes-Backend

## Table of contents
1. [Description](#description)
   1. [Application function](#application-function)
   1. [Technology choices](#technology-decisions)
   2. [Problems faced during development & Future features](#problems-and-future-features)
2. [Installation](#installation)
3. [Endpoints](#endpoints)
4. [Credits](#credits)
5. [Sources](#sources)
6. [License](#license)

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



## Credits <a name="credits" />

## Sources <a name="sources" />
* Daftari, S. (2020, 30 april). Top 10 Pros of using Django framework for back-end web development. 10 Reasons Why Django Web Development with Python is Most Popular for Backend Web Development. https://www.kelltontech.com/kellton-tech-blog/why-django-web-development-with-python-for-backend-web-development
* Django Stars. (2020, 6 november). Top 6 Django Compatible Hosting Services. Django Stars Blog. https://djangostars.com/blog/top-django-compatible-hosting-services/


## License <a name="license" />
