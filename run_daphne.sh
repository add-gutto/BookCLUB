#!/bin/bash
export DJANGO_SETTINGS_MODULE=BookCLUB.settings
export PYTHONPATH=$(pwd)
daphne -p 8000 BookCLUB.asgi:application
