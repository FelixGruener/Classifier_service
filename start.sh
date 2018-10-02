#!/bin/bash
flask db init
flask db migrate -m "initial migration"
flask db upgrade
flask run