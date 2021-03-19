#!/bin/bash

git add .
git commit -m "changes"
git push


git checkout deploymentCheese
git pull
git checkout development output.json
wait
git add .
git commit -m "update output.json" output.json
wait
git push
wait

git checkout development
