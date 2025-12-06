#!/bin/bash
poetry run ruff check --select I --fix .
poetry run ruff check --fix .
poetry run ruff format .
