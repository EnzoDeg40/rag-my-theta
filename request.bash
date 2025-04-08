#!/bin/bash

# Check if an argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <text>"
    exit 1
fi

# Assign the first argument to a variable
input_text="$1"

# Make the POST request with the provided text
curl -X POST http://127.0.0.1:8000/hotels \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"$input_text\"}"