# global_covid_cases

Note: This was a university project for a Cloud Computing module. It is a full-stack app which I dockerised and hosted on AWS using Cassandra to store and replicate data.

Summary: This is a prototype app which shows the number of confirmed coronavirus cases in a country. 
It uses a distributed database to store the result of api calls on the covid19API (https://documenter.getpostman.com/view/10808728/SzS8rjbc?version=latest); if the country you're looking for has an up-to-date record in the database, it will query the database. If not, it will request the covid19 api and update the database. 

IMPORTANT NOTE: 
POST and PUT functionalities were deliberately omitted because their functions have been integrated into the GET endpoint.
If you look at the GET endpoint, you can see that if the passed country_name parameter doesn't match a record in the database, it will automatically do an api call to the external api and add a record to the database. This is why POST was not included.
As for PUT, (again looking at the GET endpoint), the method automatically checks if the record in the database is out of date, and if so makes an api call and updates the record in the database. 
As such, only two functionalities were made, GET (which includes POST and PUT in its code) and DELETE (which deletes a record in the database if it exists).
Also, basic ssl encryption was added by using ssl_context='ad hoc' as a parameter in app.run but was removed because of conflict with Postman testing. As explained in the demonstration, this would serve the connection over https with a self-signed certificate.

Commands to create keyspace and table:

Create keyspace countries with replication = {'class' : 'SimpleStrategy', 'replication_factor' : 1};

Create table countries.cases (Name text primary key, cases int, publish_date date);













