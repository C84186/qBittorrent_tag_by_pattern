#!/bin/sh

while true; do
  python /app/synchronize_cat_tags.py
  echo "Waiting $1 seconds..."
  sleep "$1"
done

