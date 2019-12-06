# JOKE_API

Multi-user REST API service providing CRUD for jokes, using external APIs.

- [Launch app](#running-the-project-locally)
- API
  - [Get jokes](#get-my-jokes)
  - [Create joke](#create-new-joke)
  - [Get joke :id](#get-my-joke)
  - [Update joke :id](#update-my-joke)
  - [Delete joke :id](#delete-my-joke)
  - [Get random](#get-random-joke)
- Errors
  - [Without login](#request-without-login)
  - [Wrong :id](#wrong-joke-id)
  - [Joke validation](#joke-validation-error)



## Running the Project Locally

First of all
```bash
git clone https://github.com/madmaxeatfax/restapi-test.git
cd restapi-test
```

For fast setting, you can use bash script. It will:
1. Install requirements
2. Export env variables
3. Start postgresql server
4. Create db tz_app and user tester:tester
(Linux, macOS only)
```bash
source scripts/setup
# for custom params use flags
source scripts/setup -u differentUser -p userPass -d dbName
```

Here we go. Now you can run tests and flask app
```bash
source scripts/test
flask run
```

After using, you can clear traces with teardown script
```bash
source scripts/teardown
```

## Using Docker (new!)

```bash
git clone https://github.com/madmaxeatfax/restapi-test.git
cd restapi-test

docker-compose up
source scripts/test # from container

# then test manually on localhost:5000

docker-compose down
```

## Get my jokes
### Request
`GET /api/v1/jokes`

	curl -i "http://localhost:5000/api/v1/jokes?login=Gunter"

### Response

	HTTP/1.0 200 OK
	Content-Type: application/json
	Content-Length: 577
	Server: Werkzeug/0.16.0 Python/3.7.3
	Date: Sun, 13 Oct 2019 12:58:26 GMT

	{
	  "jokes": [
		{ "content": "Chuck Norris can multiply length x width x heigth when finding the circumference of a circle.",  "id": 2 },
		{ "content": "In the Bible, Jesus turned water into wine. But then Chuck Norris turned that wine into beer.", "id": 4 },
		{ "content": "Chuck Norris can make a single female cheat.",  "id": 5 }
	  ],
	  "user": { "id": 1, "login": "Gunter" }
	}


## Create new joke
### Request
`POST /api/v1/jokes`

	curl -X POST -F joke="some joke" -H "login: Gunter" -i "http://localhost:5000/api/v1/jokes"

### Response

    HTTP/1.0 201 CREATED
	Content-Type: application/json
	Content-Length: 115
	Server: Werkzeug/0.16.0 Python/3.7.3
	Date: Sun, 13 Oct 2019 12:14:52 GMT

	{
	  "joke": { "content": "some joke", "id": 1 },
	  "user": { "id": 1, "login": "Gunter" }
	}


## Get my joke
### Request
`GET /api/v1/jokes/:id`

	curl -H "login: Gunter" -i "http://localhost:5000/api/v1/jokes/1"

### Response

    HTTP/1.0 200 OK
	Content-Type: application/json
	Content-Length: 78
	Server: Werkzeug/0.16.0 Python/3.7.3
	Date: Sun, 13 Oct 2019 12:30:19 GMT

	{
	  "joke": { "content": "some joke", "id": 1 },
	  "user_id": 1
	}


## Update my joke
### Request
`PUT /api/v1/jokes/:id`

	curl -X PUT -F joke="another joke" -H "login: Gunter" -i "http://localhost:5000/api/v1/jokes/1"

### Response

    HTTP/1.0 200 OK
	Content-Type: application/json
	Content-Length: 81
	Server: Werkzeug/0.16.0 Python/3.7.3
	Date: Sun, 13 Oct 2019 12:33:17 GMT

	{
	  "joke": { "content": "another joke",  "id": 1 },
	  "user_id": 1
	}


## Delete my joke
### Request
`DELETE /api/v1/jokes/:id`

	curl -X DELETE -H "login: Gunter" -i "http://localhost:5000/api/v1/jokes/1"

### Response

    HTTP/1.0 200 OK
	Content-Type: application/json
	Content-Length: 81
	Server: Werkzeug/0.16.0 Python/3.7.3
	Date: Sun, 13 Oct 2019 12:36:18 GMT

	{
	  "joke": { "content": "another joke", "id": 1 },
	  "user_id": 1
	}


## Get random joke
### Request
`GET /api/v1/jokes/random`

	curl -H "login: Gunter" -i "http://localhost:5000/api/v1/jokes/random"

### Response

	HTTP/1.0 200 OK
	Content-Type: application/json
	Content-Length: 162
	Server: Werkzeug/0.16.0 Python/3.7.3
	Date: Sun, 13 Oct 2019 12:53:05 GMT

	{
	  "joke": { "content": "Chuck Norris can multiply length x width x heigth when finding the circumference of a circle.", "id": 2 },
	  "user_id": 1
	}

# Errors handling

## Request without login
`[GET, POST] /api/v1/jokes`
`[GET, PUT, DELETE] /api/v1/jokes/:id`
`GET /api/v1/jokes/random`

	>>> curl -i "http://localhost:5000/api/v1/jokes"

	HTTP/1.0 403 FORBIDDEN
	Content-Type: application/json
	Content-Length: 27
	Server: Werkzeug/0.16.0 Python/3.7.3
	Date: Mon, 14 Oct 2019 15:26:02 GMT

	{ "error": "Login required" }


## Wrong joke id
`[GET, PUT, DELETE] /api/v1/jokes/:id`

	>>> curl -H "login: Gunter" -i "http://localhost:5000/api/v1/jokes/1024"

	HTTP/1.0 404 NOT FOUND
	Content-Type: application/json
	Content-Length: 46
	Server: Werkzeug/0.16.0 Python/3.7.3
	Date: Mon, 14 Oct 2019 15:31:50 GMT

	{ "error": "You have no joke with id 1024" }


## Joke validation error
`PUT /api/v1/jokes/:id`
`POST /api/v1/jokes`

	>>> curl -X POST -F "form=without joke" -H "login: Gunter" -i "http://localhost:5000/api/v1/jokes"

	HTTP/1.0 400 BAD REQUEST
	Content-Type: application/json
	Content-Length: 38
	Server: Werkzeug/0.16.0 Python/3.7.3
	Date: Mon, 14 Oct 2019 15:38:18 GMT

	{ "error": "Body have no field <joke>" }⏎

	>>> curl -X POST -F "joke=666" -H "login: Gunter" "http://localhost:5000/api/v1/jokes"

	{ "error": "Wrong type for joke. Must be string" }

	>>> curl -X POST -F "joke=" -H "login: Gunter" "http://localhost:5000/api/v1/jokes"

	{ "error": "Joke is empty" }
