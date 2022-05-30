# Alert Integration Demo TOM

## Overview

This is the source code for the alerts integration demo Target Observation Manager (TOM), which features an alerts broker module that queries a SCiMMA Hopskotch topic published by our alerts integration broker companion deployment (see `/src/broker`).

## Build the Docker image

```bash
docker build -t alert-tom .
```

## Initialize the Django app with `tom_setup`

Follow directions at https://tom-toolkit.readthedocs.io/en/latest/introduction/getting_started.html.

Run the container with the source code mounted as a volume:

```bash
docker run --rm -it -p 8000:8000 -v $(pwd):/home/worker/alerts_demo alert-tom bash
```

Run `tom_setup` to initialize the TOM:

```bash
worker@fbf36e4ef4ba:~/alerts_demo$ cd alerts_demo/

worker@fbf36e4ef4ba:~/alerts_demo/alerts_demo$ python manage.py tom_setup

Welcome to the tom_setup helper script. This will help you get started with a new TOM.
DO NOT RUN THIS SCRIPT ON AN EXISTING TOM. It will override any custom settings you may already have.
Do you wish to continue? [y/N] y
Checking Python version... OK
Creating project directories... OK
Generating secret key... OK
Which target type will your project use? 1) SIDEREAL, 2) NON_SIDEREAL 1
Help messages can be configured to appear to give suggestions on commonly customized functions. If enabled now, they can be turned off by changing HINTS_ENABLED to False in settings.py.
Would you like to enable hints? [y/N] y
Generating settings.py... OK
Generating urls.py... OK
Running initial migrations... OK
Please create a Principal Investigator (PI) for your project
Username (leave blank to use 'worker'): admin
Email address: admin@localhost
Password: 
Password (again): 
This password is too common.
Bypass password validation and create user anyway? [y/N]: y
Superuser created successfully.
Setting up Public group... OK
Setup complete! Run ./manage.py migrate && ./manage.py runserver to start your TOM.
```

## Local development with Docker Compose

To run locally via Docker Compose, copy `env.sample` to `.env` and customize the parameter values as desired. Then launch the application with

```bash
cd /path/to/this/repo/clone
docker-compose up
```

By default you should be able to access the service by opening http://127.0.0.1:8000/tom/ in your browser.

To start with a clean slate, run the following to destroy the database and any other persistent volumes:

```bash
docker-compose down --remove-orphans --volumes
```

## Alerts broker module for TOM

Follow instructions at https://tom-toolkit.readthedocs.io/en/latest/brokers/create_broker.html.
