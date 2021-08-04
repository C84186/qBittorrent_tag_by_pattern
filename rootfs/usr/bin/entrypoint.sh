#!/bin/sh

while true; do
  python "/app/$2"
  echo "Waiting $1 seconds..."
  sleep "$1"
done

