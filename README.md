# capstone-1

1. What goal will your website be designed to achieve?  
My website will be a virtual store where customers can window shop and purchase various goods.

2. What kind of users will visit your site? In other words, what is the demographic of your users?  
The demographic of my users is going to be anyone who enjoys the wide variety of options that online shopping provides.

3. What data do you plan on using? You may have not picked your actual API yet, which is fine, just outline what kind of data you would like it to contain.  
&nbsp; &#8212;    Users: id, email, first name, last name, and password.  
&nbsp; &#8212;    Products: id, name, price, rating, rating_count, and description  
&nbsp; &#8212;    Carts: user_id, product_id  
&nbsp; &#8212;    Favorites: user_id, product_id  

4. In brief, outline your approach to creating your project (knowing that you may not know everything in advance and that these details might change later). Answer questions like the ones below, but feel free to add more information:  

* What does your database schema look like?  
&nbsp; &#8212;    USERS and PRODUCTS are joined by the CARTS table, USERS and PRODUCTS are also joined on the FAVORITES table  

* What kinds of issues might you run into with your API?  
&nbsp; &#8212;    Uptime is always an issue, but the number of calls is not really a problem as of now  


* Is there any sensitive information you need to secure?  
&nbsp; &#8212;    The users password should be secured  


* What functionality will your app include?  
&nbsp; &#8212;    A search function, in-app navigation and RESTful routing  


* What will the user flow look like?  
&nbsp; &#8212;    Login or sign up, see list of products, add to cart or see more details of specific products  


* What features make your site more than CRUD? Do you have any stretch goals?  
&nbsp; &#8212;    Reccomendations based off of the product details you chose to look at.  
