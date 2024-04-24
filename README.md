![waving](https://capsule-render.vercel.app/api?type=waving&height=200&text=devspoon-portfolio-blog&fontSize=60&fontAlign=50&fontAlignY=40&color=gradient)

# devspoon-portfolio-blog

This project supports the development of personal homepages such as portfolios and blogs. Based on Django, it provides advanced technologies such as Class View, Modelform, and Admin Custom. It leverages a variety of external libraries that are actually used. It use redis and celery. This project includes most of the functionality required for Django commercial services.

# introduce "Devspoon-Projects"

- We provide an open source infrastructure integration solution that can easily service Python, Django, PHP, etc. using docker-compose. You can install the commercial-level customizable nginx service and redis at once, and install and manage more services at once. If you are interested, please visit [Devspoon-Projects](https://github.com/devspoon/Devspoon-Projects).

# Navigation

- [devspoon-portfolio-blog](#devspoon-portfolio-blog)
- [Navigation](#navigation)
- [Official guide document](#official-guide-document)
- [Features](#features)
- [Development skills to get started](#development-skills-to-get-started)
- [Project understanding](#project-understanding)
  - [Home](#home)
  - [User](#user)
  - [Blog](#blog)
    - [Current category : Blog, Books, Online study, Open source, project](#current-category--blog-books-online-study-open-source-project)
  - [Board](#board)
    - [Current category : Notice, Reactivate, Visiter](#current-category--notice-reactivate-visiter)
  - [Config](#config)
- [Installing](#installing)
- [Running the tests](#running-the-tests)
- [Deployment'](#deployment)
- [Contributing](#contributing)
- [Versioning](#versioning)
- [Authors](#authors)
- [License](#license)

# Official guide document

- preparing...

# Features

- **Separated config(settings) file management** : Setting files are separated with base(common file), dev, prod, stage, test. So user can choice a condition for any server status of development.
- **Separated file management** : Normally Django provides views.py, admin.py and models.py respectively. However, it is very difficult to manage all classes and functions in one file. So this project has separated file management to show how it can be handled.
- **Replication database management** : In a distributed system, databases are created in a replicated state. So django needs a connection point for reading and writing. This project shows you how to use replica_router.py to handle cases.
- **test** : Based on pytest, using faker and factory boy. support nose
- **profiling** : Support silk
- **Github action test** : Push to github and the github action Django CD with Testing version to OCI” will run automatically.
- **github action distribute** : Push to github, go to "Django CD with staging version to OCI" in the action menu, and click "run workflow" to start deployment.
- **Redis cash** : Supports cache, session, and celery worker buffers. Most view classes use the Redis cache, and admin.py also handles when content is deleted or updated.
- **Celery** : During the account creation process, account information that is not confirmed by email for a certain period of time will be deleted.
- **Docker** : Using the [devspoon-web](https://github.com/devspoons/devspoon-web) repository. This includes nginx, unicorn, mysql, redis, monitoring, etc. refer [Devspoon-Projects](https://github.com/devspoon/Devspoon-Projects).
- **Monitoring** : Support sentry
- **email configuration** : mailgun, sendgrid, sendinblue
- **Social login** : google, kakao, naver
- **Package management** : Using poetry
- **i18n, Internationalization** : Support English and Korean

# Development skills to get started

- Front-end : Css, Javascript, Html, Bootstrap5.
- Back-end (App application) : Python3.x, Database Query, Redis, Celery.
- Framework : Django.

# Project understanding

## Home App

- Index
- Search (using django orm) / will update to haystack search.
- Main menu (django-mptt) - model only.
- Site information - model only.
- Social Account - model only (not use).

## User App

- User - AbstractUser
- Email Verification : It sends a email which has verification link
- Sending Email monitoring - model only : Supports mailgun, sendinblue, sendgrid.
- User profile : when a user register website, is created automatically.
- Login : Supports local and social account logins (django-allauth).

## Blog App

### Current category : Blog, Books, Online study, Open source, project

- Separate files in each folder by category name (admin, models, views, test).
- All categories have a similar structure for easy understanding. This allows users to expand new categories by copying and pasting. But it's not good for manage code.
  Using init function of "class view" or "function view", user can consider repactoring this one.
  But doesn't deal with in this project.
- A blog model designed based on an abstract architecture.
- A blog_reply designed based on an abstract architecture.
- Almost category's reply in views files are response to json. (Request and response, UI processing with JavaScript.)

## Board App

### Current category : Notice, Reactivate, Visiter

- It is similar to the blog app, the design of the 'model' is different, and the app is separated for the purpose of expanding the 'view' function and separating the 'administrator' menu.

## Portfolio App

- This page provides portfolio information for the site owner or administrator. This is a service that displays development history, projects, learning, areas of interest, etc. on one page.

## ETC

### router

- There is replica_router.py in the core folder.
- Define the DB to operate for reading, writing, and migration. default is “write db” and Replica1 is “read db”.

### middleware

- It is in the common folder of the custom_middlewares app.
- There are two statistical functions: The first is "Connection Method Statistics", which collects the user's Windows, Mac, Android, etc., and the second is "Connection Hardware Statistics", which collects the user's Mobile, Tablet, PC, etc. You can check this information on the administrator page.

### common

- There is a separate file where the redis decorator and redis functions are defined, and there is also a file that custom-manages 400, 403, 404, 500, and CSRF errors.

### celery

- There is a celery_etc folder that controls celery and celery-beat.
- Celery tasks are defined in your app's task.py. Users who have not verified their email address for a certain period of time are automatically deleted at regular intervals using celery-beat.

## Config

- The settings folder contains fragmented files and folders for each service. So users can easily included any service they want by using 'Import'.
- The current settings folder contains files for 5 cases: Basic, Development, Test, Stage, and Product. For all settings, user must include the base file that is default file.
- You can copy the '.env' file information at [.env](https://devspoon.tistory.com/167)
  - When the project's .env is updated, the post is automatically updated.

# Installing

- Install requirement file using pip
  - The existing pip management method has been changed to the "poetry" management method, and pip provides a development setup environment only on Windows.
    ```
    pip install -r requirements/dev.txt
    ```
- Install using poetry
  - Install only default and dev
    ```
    poetry install --without test,stage --no-root
    ```

# Running the tests

- Using pytest.ini
  ```
  pytest
  ```

# Deployment

- Related files are in .github/workflows.
- You can test and deploy using github tasks. You can define information directly on GitHub by referring to "secret" or [.env](https://devspoon.tistory.com/167).

# Contributing

Please read [CONTRIBUTING.md](https://github.com/devspoon/devspoon-portfolio-blog/blob/main/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

# Versioning

We use [SemVer](https://semver.org/ "SemVer") for versioning. For the versions available, see the [tags on this repository](https://semver.org/ "repository tag").

# Authors

- Lim DoHyun - Owner

# License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/devspoon/devspoon-portfolio-blog/blob/main/LICENSE) file for details
