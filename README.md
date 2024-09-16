[![Actions Status](https://github.com/sergey-royt/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/sergey-royt/python-project-83/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/5da3461e840fd0963c66/maintainability)](https://codeclimate.com/github/sergey-royt/python-project-83/maintainability)

## Page analyzer

### Description
This is a Python web app uses Flask framework
which provides simple features to check websites SEO-accessibility.

### How it works
On this app, you can add sites to the main page by entering a URL, 
perform "SEO checks" to receive basic information about it. 
Users can add as many websites and checks as they want.

### Demo
You can try the app in [web](https://page-analyzer-vqqh.onrender.com/).
___

**Installation**:
1. Clone repository
2. Create postgresql db using provided cheatsheet (database.sql)
3. Create .env file in repository directory and set up variables 
- `SECRET_KEY` (for Flask sessions)
- `DATABASE_URL` ({provider}://{user}:{password}@{host}:{port}/{db})
- You can specify min and max count of database connections by adding `MINCONN={int}` and `MAXCONN={int}`
by default minconn=2, maxconn=3
4. Run `make build`
5. Run `make dev` for debugging (with WSGI debug set to 'True'), or `make start` for production (using gunicorn)

[Try in web](https://page-analyzer-vqqh.onrender.com)
