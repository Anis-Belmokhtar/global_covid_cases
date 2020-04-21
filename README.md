# global_covid_cases

Summary: This is a prototype app which shows the number of confirmed coronavirus cases in a country. 
It uses a distributed database to store the result of api calls on the covid19API (https://documenter.getpostman.com/view/10808728/SzS8rjbc?version=latest); if the country you're looking for has an up-to-date record in the database, it will query the database. If not, it will request the covid19 api and update the database. 

Commands to create keyspace and table:

Create keyspace countries with replication = {'class' : 'SimpleStrategy', 'replication_factor' : 1};

Create table countries.cases (Name text primary key, cases int, publish_date date);








