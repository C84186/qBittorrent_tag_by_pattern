#!/bin/sh

echo "Initital synchronization"
python /app/synchronize_cat_tags.py

echo "Done initial sync"



while true; do
  echo "Waiting $1 seconds..."
  sleep "$1"
  python /app/synchronize_cat_tags.py

done


