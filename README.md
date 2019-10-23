# Deployment
## Run MySQL Server
Run MySQL Server before start the app.

## Configure database
`/mechanics_api/mysql.cnf` is database configuration file.\
`database` is database name for using.\
`host` is MySQL Server url.\
`port` is MySQL Server port.\
`user` is MySQL login username.\
`password` is MySQL login password.

## Create environment and Install dependencies
1. Run command `python -m venv env`.
1. Use virtual environment.
    - Windows: `env\Scripts\activate`.
    - Linux/OS X: `. env/bin/activate`.
1. Run command `python -m pip install --upgrade pip` to ensure latest pip.
1. Run command `pip install -r requirements.txt` to install dependencies.

## Migrate database
Run command `python manage.py migrate app 0001`.\
Ensure that database is empty with no tables before run this command.

## Run Django Server
Run command `python manage.py runserver`.

## Local Test
If test in local environment, add `127.0.0.1` to `ALLOWED_HOSTS` in `settings.py`.

# Verification
## Load sample data
Run command `python manage.py loaddata data/app.json`.\
Ensure that Migrate database have done and all tables are empty before run this command.

## Set postman
1. Open postman.
1. Import `MechanicsAPI.postman_collection.json`.
1. Import `MechanicsAPI.postman_environment.json`.

## Postman environment
`host`: api host url.\
`admin-token`: admin user token.\
`standard-token`: standard user token.\
`invalid-token`: invalid user token.

## Verification
Send postman request top to bottom.\
Sample data is ready for non-stop verification with postman.

## Authorization tokens
### Admin
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6ImFkbWluQGV4YW1wbGUuY29tIiwiaWQiOjEsIm5hbWUiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsInRodW1ibmFpbFVybCI6bnVsbH0.3Aq4TFin4OwWEgaHzRQf2ClJ_CM-L7cvUpqiH-CRBIo

### Standard
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InN0YW5kYXJkQGV4YW1wbGUuY29tIiwiaWQiOjIsIm5hbWUiOiJzdGFuZGFyZCIsInJvbGUiOiJzdGFuZGFyZCIsInRodW1ibmFpbFVybCI6bnVsbH0.qgYGdQ-Nazj3f3dBxmvgXXIJDFNWwoIXeWpcdo0BXGY