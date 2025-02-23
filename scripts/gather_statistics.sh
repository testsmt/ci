#! /bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <directory> <output_file>"
    exit 1
fi

dir="$1"
output_file="$2"
unsoundness_found=false
export UNSOUNDNESS_FOUND=false

# Loop through each .sqlite3 file in the directory
for db in "$dir"/*.sqlite3; do
    echo "Processing database: $db"

    filename=$(basename -- "$db")
    file_identifier="${filename%.sqlite3}"

    # Get the unique solver configurations
    unique_solver_configs=$(sqlite3 "$db" "SELECT COUNT(DISTINCT solver_cfg) FROM ExpResults;")

    # Queries to collect statistics
    echo "Distinct Results:"
    sqlite3 "$db" "SELECT DISTINCT(result) FROM ExpResults;"

    for status in "unsat" "sat" "timeout" "rejected" "crash" "unsoundness" "unknown"; do
        count=$(sqlite3 "$db" "SELECT COUNT(*) FROM ExpResults WHERE result='$status';")
        percentage=$(awk "BEGIN { printf \"%.2f\", ($count / ($unique_solver_configs * $NUM_TESTS)) * 100 }")
        echo "Count of '$status': $count ($percentage%)"

        if [ "$status" == "unsoundness" ] && [ "$count" -gt 0 ]; then
            UNSOUNDNESS_FOUND=true
            sqlite3 "$db" "SELECT formula_idx FROM ExpResults WHERE result='unsoundness';" | while read -r formula_idx; do
                echo "$formula_idx, $file_identifier, $(date '+%Y-%m-%d %H:%M:%S')" >> "$output_file"
            done
        fi
    done

    echo "Unique Solver Configurations: $unique_solver_configs"
    echo "---------------------------------------------"
done

echo "UNSOUNDNESS_FOUND=$UNSOUNDNESS_FOUND" >> $GITHUB_ENV
echo "Statistics collection complete."