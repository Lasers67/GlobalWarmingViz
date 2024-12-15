#!/bin/bash
cd src
gunicorn -b 0.0.0.0:8000 main:app
