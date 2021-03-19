#!/bin/bash

git commit output.json -m "output.json"
git push
git checkout deploymentCheese
git checkout development output.json

git pull
git checkout development