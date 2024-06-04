#!/bin/bash

rm setup.py
rm -rf virty-api-client
sudo rm -rf virty.egg-info
rm -rf api
sudo rm -rf build
rm -rf models

sudo rm -rf virty

openapi-python-client generate --url https://virty-dev.hinagiku.me/api/openapi.json

sudo mv ./virty-api-client/virty_api_client virty
rm -rf virty-api-client