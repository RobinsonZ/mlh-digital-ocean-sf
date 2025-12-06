#!/bin/bash

poetry run pyright --level warning
uvx ty check

poetry run ruff check --select I --fix .
poetry run ruff check --fix .
poetry run ruff format .
