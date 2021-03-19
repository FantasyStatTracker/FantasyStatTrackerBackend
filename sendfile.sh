#!/bin/bash

git commit output.json -m "output.json"
git push origin deploymentCheese

git checkout deploymentCheese
git pull
git checkout development