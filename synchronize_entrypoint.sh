#!/bin/sh

echo "Initital synchronization"
python /app/synchronize_cat_tags.py

echo "Done initial sync"
exec "$@"
