# People

This project runs a python flask server that reads a CSV file of people into a MySQL database, and
opens up REST access to the following endpoints:

1. `GET /ping` which returns "pong" ensuring the server is alive and responding to requests
2. `GET /people` which returns a JSON representation of all people ever created
3. `GET /people/age` which returns a JSON representation of all peoeple ever created sorted by age from youngest to oldest
4. `GET /ids/lastname/<lastname>` which returns a JSON representation of all `ids` belonging to any people with this <lastname>
5. `POST /people/person` which adds the specified person to the MySQL databasse and then returns a JSON representation of all people

# POST /people/person API

Input parameters (to be sent as application/json data with the request body):

`age`
`id`
`first`
`last`
`githubacct`
`date of third grade graduation`

All fields are optional, and any additional fields will be ignored.

Here is an example request and response:

```
curl http://localhost:9000/people/person -d '{"first": "david", "last": "piteraagain", "age": 100, "id": 102, "githubacct": "dpitera", "date of third grade graduation": "1/15/2000"}'
{
  "result": [
    {
      "age": 22,
      "date of third grade graduation": "6/25/01",
      "first name": "Matt",
      "github account": "wr0ngway",
      "id": 1,
      "last name": "Conway"
    },
    {
      "age": 76,
      "date of third grade graduation": "6/24/40",
      "first name": "David",
      "github account": "",
      "id": 2,
      "last name": "Block"
    },
    {
      "age": 16,
      "date of third grade graduation": "6/25/07",
      "first name": "",
      "github account": "",
      "id": 3,
      "last name": "Robiner"
    },
    {
      "age": null,
      "date of third grade graduation": "6/25/88",
      "first name": "Rob",
      "github account": "",
      "id": 4,
      "last name": "May"
    },
    {
      "age": 30,
      "date of third grade graduation": "",
      "first name": "Jason",
      "github account": "haruska",
      "id": 5,
      "last name": ""
    },
    {
      "age": 25,
      "date of third grade graduation": "1/1/03",
      "first name": "Alex",
      "github account": "a-rob",
      "id": 6,
      "last name": "Robiner"
    },
    {
      "age": 50,
      "date of third grade graduation": "3/26/70",
      "first name": "Lawrence",
      "github account": "",
      "id": 7,
      "last name": "Robiner"
    },
    {
      "age": null,
      "date of third grade graduation": "",
      "first name": "david",
      "github account": "",
      "id": 8,
      "last name": "pitera"
    },
    {
      "age": null,
      "date of third grade graduation": "10/22",
      "first name": "david",
      "github account": "dpitera",
      "id": 9,
      "last name": "pitera"
    },
    {
      "age": null,
      "date of third grade graduation": "",
      "first name": "david",
      "github account": "",
      "id": 10,
      "last name": "pitera"
    },
    {
      "age": null,
      "date of third grade graduation": "",
      "first name": "david",
      "github account": "",
      "id": 11,
      "last name": "piteraagain"
    },
    {
      "age": 100,
      "date of third grade graduation": "",
      "first name": "david",
      "github account": "",
      "id": 100,
      "last name": "piteraagain"
    },
    {
      "age": 100,
      "date of third grade graduation": "",
      "first name": "david",
      "github account": "",
      "id": 101,
      "last name": "piteraagain"
    },
    {
      "age": 100,
      "date of third grade graduation": "1/15/2000",
      "first name": "david",
      "github account": "dpitera",
      "id": 102,
      "last name": "piteraagain"
    }
  ],
  "status": 200
}
```

# Configuration and Set Up

First we need to install and run MySQL:

```
brew install mysql
brew services start mysql
pip install MyDSQLdb
```

Then we need to create our user `username` with password `password` and then create our database `people` and table `person`.

```
mysql -uroot
```

Once inside the MySQL REPL:

```
GRANT ALL PRIVILEGES ON *.* TO 'username'@'localhost' IDENTIFIED BY 'password';
CREATE DATABASE people;
USE people;
CREATE TABLE PERSON (ID INT AUTO_INCREMENT PRIMARY KEY, FIRST_NAME VARCHAR(255), LAST_NAME VARCHAR(255), AGE INT, GITHUB_ACCOUNT VARCHAR(255), DATE_OF_THIRD_GRADE_GRADUATION VARCHAR(255));
```

# Running the server

`python server.py <available_port_number> <valid_csv_file> <optional -d argument for debug mode>`

Example:

`python server.py 9000 people.csv -d`

Then you can access the REST endpoints at `http://localhost:9000`.

# MySQL DataModel Design Decisions

1. The ID is an `int` and the primary key, and is set to auto_increment, meaning if users do not specify one, it will be created for them in an incremented fashion.
2. Age is an `int`
3. All other fields associated with a person are `varchar(255)`, or strings.

# How to Improve the MySQL Data Model

1. The "date of third grade graduation" should really be stored as a DATE type in the database.
2. Create indexes for faster lookups for any field by which we think we will search often.

# How to Improve the Application

1. Refactor the code-base, i.e. ideally all db interactions would take place in their own module, all notions of a "person" and how that is translated to SQL would be contained in its own module, etc.

2. Implement authentication and authorization.

3. Automatically initialize the MySQL database, tables, etc in the app so the application. Part of this work should include properly handling the configuration data and not just injecting it in the server.py.

4. Fix the improper "ID" field serialization bug as it is read in from the `people.csv` file.

5. Fix error handling for interactions with the database, i.e. implementing a retry strategy or ensuring failed loads are added to a queue and retried at a later time, updating rows that already exist with new data, etc.

6. Implement unit tests and integration tests. I generally find for RESTful servers that IT tests are easier to implement and can test just about everything, so I would start there by testing different input and expected output.

7. Implement better input validation when reading from file and when reading RESTful input.

8. Separate this application into 2 applications: 1 that just runs the RESTful server and 1 that just handles a bulk upload (i.e. reads from the file). If this file is large, it might be a while before the REST endpoints are able to listen. Furthermore, we can implement BATCH uploads when we do the bulk load, and gain increased performance throughput by parallelizing the load.

9. Test what happens when there are billion of users and a user calls `GET /people`. There are two things I am concerned with: 1. memory limits, i.e. do we need to paginate the results back from MySQL? and 2. Server blocking, i.e. do we need to implement asynchronous processing so the server can process other requests while it responds to a longer running query.

10. Fully document all endpoints, input and output.

11. Ensure the database and the application are both highly available, i.e. we want our application to be horizontally scalable (therefore access to it should probably be preceeded by HAProxy and keepalive layer), and we want our database to include multiple replicas to be able to decrease the risk of dataloss and unavailability. Master failover in MySQL has many options, but IMO the best option tends to be master-slaves setup with Orchestrator as the master failover automater. If this does not suffice, there are other options (Group Replication, master-master Galera bakced implementations, MHA, etc), and there is always the option to use a different database.
