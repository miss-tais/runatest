# Runatest app #

## Project Setup

Ensure that `docker` and `docker-compose` is installed

```
$ git clone git@github.com:miss-tais/runatest.git
$ cd runatest
```

Then create `.env.django.local` file with the following settings:

```
DJANGO_SETTINGS_MODULE=config.settings.local
SECRET_KEY=your-secret-key
DB_NAME=database-name
DB_USER=database-user
DB_PASSWORD=database-password
DB_HOST=postgres
DB_PORT=5432
```

Create `.env.postgres.local` file with the following settings:

```
POSTGRES_NAME=database-name
POSTGRES_USER=database-user
POSTGRES_PASSWORD=database-password
```

Run

```
$ docker-compose --f docker-compose.local.yml up -d --build
```

## Examples

POST /categories/ API endpoint. Endpoint accepts json body

```
curl -X POST -H "Content-Type: application/json" -H 'Accept: application/json' -d '{"name":"Category 1","children":[{"name":"Category 1.1","children":[{"name":"Category 1.1.1"}]},{"name":"Category 1.2"},{"name":"Category 1.2.2"}]}' http://localhost:8000/categories/ 
```

GET /categories/`<id>`/ API endpoint. Endpoint retrieves category name, parents (and their parents), 
children and siblings by primary key (`<id>`) in json format

```
curl -X GET "http://localhost:8000/categories/2/"
```
