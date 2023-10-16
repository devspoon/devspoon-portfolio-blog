![waving](https://capsule-render.vercel.app/api?type=waving&height=200&text=devspoons-portfolio-blog&fontSize=60&fontAlign=50&fontAlignY=40&color=gradient)

# devspoons-portfolio-blog

This project that supports the development of personal homepages for portfolios and blogs. based on django that uses class views with separated views, models, admin can help you with advanced learning and practice of django.

# Navigation

- [devspoons-portfolio-blog](#devspoons-portfolio-blog)
- [Navigation](#navigation)
- [Official documentation](#official-documentation)
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

# Official documentation

- preparing...

# Features

- **Separated config(settings) file management** : Setting files are separated with base(common file), dev, prod, stage, test. So user can choice a condition for any server status of development.
- **Separated file management** : Normally Django provides views.py, admin.py and models.py respectively. However, it is very difficult to manage all classes and functions in one file. So this project has separated file management to show how it can be handled.
- **Replication database management** : In a distributed system, databases are created in a replicated state. So django needs a connection point for reading and writing. This project shows you how to use replica_router.py to handle cases.
- **Unit test** : developing - will use pytest, faker and factory boy
- **profiling** : developing - silk, linesman
- **Github action test** : developing.
- **Redis cash** : developing - cash, session, celery worker buffer.
- **Celery** : developing - will work with redis.
- **Docker** : developing - will include nginx, unicorn, mysql, redis, monitoring etc.
- **Distributed system** : developing - mysql replication, infra monitoring etc.
- **Multi cloud support** : developing - oracle cloud, AWS.
- **github action distribute** : developing - oracle cloud, AWS.
- **Monitoring** : developing - django, db, docker, infra condition etc.

# Development skills to get started

- Front-end : Css, Javascript, Html, Bootstrap5.
- Back-end (App application) : Python3.x, Database Query, Redis, Celery.
- Framework : Django.

# Project understanding

## Home

- Index
- Search (using django orm) / will update to haystack search.
- Main menu (django-mptt) - model only.
- Site information - model only.
- Social Account - model only (not use).

## User

- User - AbstractUser
- Email Verification : It sends a email which has verification link
- Sending Email monitoring - model only : Supports mailgun, sendinblue, sendgrid.
- User profile : when a user register website, is created automatically.
- Login : Supports local and social account logins (django-allauth).

## Blog

### Current category : Blog, Books, Online study, Open source, project

- Separate files in each folder by category name (admin, models, views, test).
- All categories have a similar structure for easy understanding. This allows users to expand new categories by copying and pasting. But it's not good for manage code.  
  Using init function of "class view" or "function view", user can consider repactoring this one.  
  But doesn't deal with in this project.
- A blog model designed based on an abstract architecture.
- A blog_reply designed based on an abstract architecture.
- Almost category's reply in views files are response to json. (Request and response, UI processing with JavaScript.)

## Board

### Current category : Notice, Reactivate, Visiter

- It is similar to the blog app, the design of the 'model' is different, and the app is separated for the purpose of expanding the 'view' function and separating the 'administrator' menu.

## Config

- The settings folder contains fragmented files and folders for each service. So users can easily included any service they want by using 'Import'.
- The current settings folder contains files for 5 cases: Basic, Development, Test, Stage, and Product. For all settings, user must include the base file that is default file.
- You can copy the '.env' file information at [.env](https://devspoon.tistory.com/167)
  - When the project's .env is updated, the post is automatically updated.

# Installing

- Install requirement file using pip
  - Requirement folder has 4 case of file : dev.txt, test.txt, stage.txt, prod.txt
    - stage.txt can be same with prod.txt. Users should make their own modifications according to the conditions of testing and monitoring of the server and infrastructure.
    - development environment setting : consider local server or one or two of CURD database.
      ```
      pip install -r requirements/dev.txt
      ```
    - test environment setting : test and profiling.
      ```
      pip install -r requirements/test.txt
      ```
    - stage environment setting : infra and integration test. can include performance test.
      ```
      pip install -r requirements/stage.txt
      ```
    - product environment setting : clean install for real service.
      ```
      pip install -r requirements/prod.txt
      ```

# Running the tests

- Using pytest.ini
  ```
  pytest
  ```

# Deployment'

- It is not covered in this project. Refer to following project.
  - preparing...

# Contributing

Please read [CONTRIBUTING.md](https://github.com/devspoon/devspoon-portfolio-blog/blob/main/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

# Versioning

We use [SemVer](https://semver.org/ "SemVer") for versioning. For the versions available, see the [tags on this repository](https://semver.org/ "repository tag").

# Authors

- Lim DoHyun - Owner

# License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/devspoon/devspoon-portfolio-blog/blob/main/LICENSE) file for details
