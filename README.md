# Prescriptions API

![example workflow](https://github.com/laurogama/prescription_api/actions/workflows/workflow.yml/badge.svg)

The api can be found on [https://gentle-harbor-62875.herokuapp.com](https://gentle-harbor-62875.herokuapp.com)

## Install

The project requires

* [Docker ](https://docs.docker.com/)
* [Docker Compose ](https://docs.docker.com/compose/)
* [Python 3.6+](https://www.python.org/)

### Steps for development

* Clone this repository
* create the files
    * .env.dev
    * .env.prod
    * .env.prod.db
    * build the docker images

## Testing

The unit tests can be executed manually with:

    $ docker-compose -f docker-compose.yml exec web coverage run

And the coverage report can be shown with:

    $  docker-compose -f docker-compose.yml exec web coverage report

The tests are also executed by Github Actions CI on Push

## Running

To test the in the production environment execute

    $ docker-compose -f docker-compose.prod.yml down -v
    $ docker-compose -f docker-compose.prod.yml up -d --build
    $ docker-compose -f docker-compose.prod.yml exec web python app.py create_db