#!/bin/bash
find . -name "*.blend[0-9]*" -type f -delete
poetry run ruff check --select I --fix .
poetry run ruff check --fix .
poetry run ruff format .
