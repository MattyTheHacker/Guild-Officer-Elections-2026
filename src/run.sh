#!/bin/bash

# go to the right directory
cd "$(dirname "$0")"

# Pull any changes
git fetch --all

# Reset the local repository to match the remote repository
git reset --hard origin/main

# Create needed directories first
mkdir -p ../data/db ../data/json/raw ../data/csv
touch ../data/db/all_data.db

# Run the application
python3 main.py

# Add all files to git
git add --all

# Commit changes
git commit -m "Update"

# Push changes to GitHub
git push
