#! /bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

dir="$1"

# Loop through each .sqlite3 file in the directory
for db in "$dir"/*.sqlite3; do
    echo "Processing database: $db"

    # Get the unique solver configurations
    unique_solver_configs=$(sqlite3 "$db" "SELECT COUNT(DISTINCT solver_cfg) FROM ExpResults;")

    # Queries to collect statistics
    echo "Distinct Results:"
    sqlite3 "$db" "SELECT DISTINCT(result) FROM ExpResults;"

    for status in "unsat" "sat" "timeout" "rejected" "crash" "unsoundness" "unknown"; do
        count=$(sqlite3 "$db" "SELECT COUNT(*) FROM ExpResults WHERE result='$status';")
        percentage=$(awk "BEGIN { printf \"%.2f\", ($count / ($unique_solver_configs * $NUM_TESTS)) * 100 }")
        echo "Count of '$status': $count ($percentage%)"
    done

    echo "Unique Solver Configurations: $unique_solver_configs"
    echo "---------------------------------------------"
done

echo "Statistics collection complete."
