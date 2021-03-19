#!/bin/bash

git add .
git commit -m "changes"
git push

git checkout deploymentCheese
git pull
git checkout development output.json
git add .
git commit -m "update output.json" output.json
git push

git checkout development