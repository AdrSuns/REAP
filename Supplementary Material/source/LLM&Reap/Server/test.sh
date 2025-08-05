#!/bin/bash

# Define the URL of your Flask application
url="http://localhost:5009/infer"

# Define the JSON payload
data='{"user_message": "Your test message here"}'

# Initialize variables to calculate the total response time
total_time=0
count=1000

# Loop to send the request 1,000 times
for i in $(seq 1 $count); do
    # Measure the time taken for the request
    start_time=$(date +%s%3N)  # Start time in milliseconds
    response=$(curl -s -o /dev/null -w "%{time_total}" -X POST -H "Content-Type: application/json" -d "$data" "$url")
    end_time=$(date +%s%3N)  # End time in milliseconds

    # Calculate the duration
    duration=$((end_time - start_time))

    # Add the duration to the total time
    total_time=$((total_time + duration))

    # Output the duration for this request
    echo "Request $i took $duration ms"
done

# Calculate the average response time
average_time=$((total_time / count))
echo "Average response time over $count requests: $average_time ms"
