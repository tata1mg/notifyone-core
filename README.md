## Introduction
This repository is the part of the open source [NotifyOne](https://github.com/tata1mg/notifyone) project.

`notifyone-core` provides core implementation in the NotifyOne project.

`notifyone-core` sits at the heart of the [NotifyOne](https://github.com/tata1mg/notifyone) project and implements the core components of the notification system. 

**Core components** - 
* `App` and `Event` creation
* `Template` creation and editing (it's the main backend service for the NotifyOne CMS)
* Template rendering 
* Triggering notifications using the handlers
* Notifications logging and status updates


### Tech Stack 
* **Python** - version 3.9.10
* **Database** - Postgres (version >= 12.x)
* **Framework** - [torpedo](https://github.com/tata1mg/torpedo) [ A lightweight wrapper around the open source [Sanic](https://sanic.dev/en/) framework ]
* **ORM** - Open source [Tortoise](https://tortoise.github.io/) ORM


### Tools & Technologies

* **[Redis](https://redis.io/docs/getting-started/)** - for caching various data inorder to operate efficiently
* **[AWS SQS](https://aws.amazon.com/sqs/)** - for asynchronous processing of the notifications and status updates
* **[AWS S3](https://aws.amazon.com/s3/)** - for storing the actual content sent to the recipients (email content, sms content etc.)
* **[Sanic OpenApi](https://github.com/sanic-org/sanic-openapi)** - for automatic OAS3 documentation of the APIs & out of the box Swagger UI

## Configurations Available
For the list of all available keys, checkout the [Config Template](https://github.com/tata1mg/notifyone-core/blob/master/config_template.json) file.

[Config Template](https://github.com/tata1mg/notifyone-core/blob/master/config_template.json) provides a template (actual keys, dummy values) for the actual config file.

The actual config.json file must be generated by the service owner with the real values. 

#### Config Keys
    config.NAME     : Name of the service
    config.HOST     : Host name for interface binding. Default value - 0.0.0.0
    config.PORT     : Port for the service
    config.WORKER   : Number of Sanic works. Default is 1
    config.DEBUG    : Available values [true/false]. If set to true, the service runs in DEBUG mode
    config.TIMEOUT  : Default timeout for all the http APIs exposed
    config.SENTRY   : Sentry configuraition details. Leave it empty if sentry integration is not needed
    config.APM      : APM configurtion. Leave it empty if APM integration is not needed

    cofig.DB_CONNECTIONS    : Holds the Postgres database connection and model details. 
                                Check for config_template.json file for all the keys available.
                                Only the below values must be provided in the config.josn file (rest of the values should be kept same) - 
                                    > config.DB_CONNECTIONS.connections.default.credentials.database
                                    > config.DB_CONNECTIONS.connections.default.credentials.host
                                    > config.DB_CONNECTIONS.connections.default.credentials.port
                                    > config.DB_CONNECTIONS.connections.default.credentials.user
                                    > config.DB_CONNECTIONS.connections.default.credentials.password

    config.REDIS_CACHE_HOSTS : Redis host and port details

    config.NOTIFICATION_REQUEST : Details about the notification requests subscription.
                                    SQS credentials and Queue details to subscribe the notification requests publised from the gateway.
        > config.NOTIFICATION_REQUEST.SQS : SQS credentials.
        > config.NOTIFICATION_REQUEST.SUBSCRIBE_TO : queues details for different priorites

    config.DISPATCH_NOTIFICATION_REQUEST : Dispatchers details. Dispatcher queues and http host for different channels.
        > config.DISPATCH_NOTIFICATION_REQUEST.SQS : SQS credentials
        > config.DISPATCH_NOTIFICATION_REQUEST.EMAIL : email queue and handler host 
        > config.DISPATCH_NOTIFICATION_REQUEST.SMS : sms queue and handler host
        > config.DISPATCH_NOTIFICATION_REQUEST.PUSH : push queue and handler host
        > config.DISPATCH_NOTIFICATION_REQUEST.WHATSAPP : whatsapp queue and handler host

    config.SUBSCRIBE_NOTIFICATION_STATUS_UPDATES : Queue details to subscribe status updates from the handlers
        > SUBSCRIBE_NOTIFICATION_STATUS_UPDATES.SQS : SQS credentials
        > SUBSCRIBE_NOTIFICATION_STATUS_UPDATES.SUBSCRIBE_TO : Queue name and subscribers count
        > SUBSCRIBE_NOTIFICATION_STATUS_UPDATES.SUBSCRIBE_DELAY_SECONDS: Delay in seconds before the subscribers are started after the service start

    config.CONTENT_LOG : AWS S3 details. This is used to log the actual notification content sent
    
    config.TEST_ENVIRONMENT : Set to `true` for non production environments (default is `false`).
                                If set to `true`, config.TEST_ALLOWED_EMAILS and config.TEST_ALLOWED_MOBILES can be used to rescrict the notification to only the allowed recipients.
    config.TEST_ALLOWED_EMAILS : List of email ID whitelisted on test environments (config.TEST_ENVIRONMENT = true)
    config.TEST_ALLOWED_MOBILES : List of mobile numbers whitelisted on test environments (config.TEST_ENVIRONMENT = true)
    config.PROVIDERS.ENCRYPTION : Contains config.PROVIDERS.ENCRYPTION.KEY and config.PROVIDERS.ENCRYPTION.AES_IV for AES encryption used to encrypt Providers configuration details     

## Setup - stand-alone and container based deployments
#### Stand-alone deployment
    1. git clone https://github.com/tata1mg/notifyone-core.git
    2. cd notifyone-core
    3. touch config.json
    4. Generate actual keys and values for config.json file. Refer to config_template.json for keys.
    5. pip isntall pipenv (if not alread installed)
    6. python3 -m pipenv shell
    7. python3 -m pipenv install
    8. python3 database.py upgrade
    8. python3 -m app.service
#### Docker container based deployment
###### Here, we pre-assume that you have got docker installed on you system and it's up and running
    1. git clone https://github.com/tata1mg/notifyone-core.git
    2. cd notifyone-core
    3. touch config.json
    4. Generate actual keys and values for config.json file. Refer to config_template.json for keys.
    5. docker build . --tag notifyone-core --build-arg SERVICE_NAME=notifyone_core
    6. docker run -p <service-port>:<service-port> --detach --name notifyone-core notifyone-core
    # (Step 7 & 8) Run DB migrations. Exec into the notifyone-core container and run the command 
    7. docker exec -it $(docker ps | grep notifyone-core | awk '{print $1}') /bin/bash
    8. python3 database.py upgrade
    9. Exit the continer

## Database Migrations 
We have wrapped the open source `aerich` tool to manage DB migrations for this project.
You can use the [database.py](https://github.com/tata1mg/notifyone-core/blob/master/database.py) script to do the migrations related stuff.
Please see the [database.py](https://github.com/tata1mg/notifyone-core/blob/master/database.py) help section by running  - **python3 database.py ---help**

## Setting up an App and an Event for testing
An important and mandatory step after setting up the service and before start sending the notifications is to register an app and create and events in the system.
Please follow below steps to create and test your first event - 

* **Create an App** - As events in the system are linked to apps, we need to create an app first. An app can be created using the "Create App" API. Please refer to the API documentation for more details
  * Sample curl request

  ```curl
    curl -X 'POST' \
      'http://0.0.0.0:9962/apps' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
          "name": "test_app",
          "info": {
            "email": {
              "sender_name": "Tata 1mg",
              "sender_address": "sender@xyzmail.com",
              "reply_to": "reply@xyzmail.com"
            }
          }
      }'
  
* **Create an Event** - create an event
  * Sample curl
  ```curl
  curl -X 'POST' \
  'http://0.0.0.0:9962/event/create' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "event_name": "test_event",
  "app_name": "test_app",
  "email": {
    "description": "This is test event",
    "subject": "Regarding your Order {{body.order_id}}",
    "content": "Your order {{body.order_id}} has been processed"
  },
  "sms": {
    "content": "Your order {{body.order_id}} has been processed"
  },
  "push": {
    "title": "Order update",
    "body": "Order {{body.order_id}} has been delivered"
  },
  "whatsapp": {
    "name": "order_delivered"
  },
  "priority": "high",
  "event_type": "transactional",
  "user_email": "test@test.com"
  }'

* **Trigger Notifications** - After you created an event, you can use [notifyone-gateway](https://github.com/tata1mg/notifyone-gateway)'s send-notification API to start triggering the notifications.

## API Document
We have used [sanic_openapi](https://github.com/sanic-org/sanic-openapi) to automatically generate the OAS3 specification API documents for the APIs exposed in this service.

Once you are done with the service setup, the API documentation can be accessed at - **{{service-host}}:{{service-port}}/swagger**

Example - If you started your service at port number 9401, the documentation can be accessed at - **localhost:9401/swagger**

#### **Alternatively,**
If you wish to have a look at the API documentation without deploying the service, you can use an independent swagger UI to view the documentation by pointing the swagger UI to the [api_doc.json](https://raw.githubusercontent.com/tata1mg/notifyone-core/master/api_doc.json) file.

Or, import the [api_doc.json](https://raw.githubusercontent.com/tata1mg/notifyone-core/master/api_doc.json) file into Postman as OAS3 API collection.



## Contribution guidelines
Please refer to our [Contribution Guidlines](https://github.com/tata1mg/notifyone-core/blob/master/CONTRIBUTING.md) before for more details.

## License
This project is licensed under the
[Apache-2.0](https://github.com/tata1mg/notifyone-core/blob/master/LICENSE) License.