#!/bin/bash

if [ ! "$#" -eq 3 ]; then
    echo "Usage: $0 <theory> <num_tests> <solvers_cfg_path>"
    exit 2
fi

theory=$1
num_tests=$2
timeout=8.0
memout=1048576
solvers_cfg_path=$3  # Corrected from $5 to $3
num_cores=4
result_dir="./results"


# Debugging: List contents of the results directory
echo "Listing contents of $result_dir:"
ls "$result_dir"

# Debugging: List contents of the specific theory directory
echo "Listing contents of $result_dir/$theory:"
ls "$result_dir/$theory"

# Debugging: List contents of the temp directory
echo "Listing contents of $result_dir/$theory/temp:"
ls "$result_dir/$theory/temp"

# Iterate over each .smt2 file in the specified directory
find $result_dir/$theory/temp -name "*.smt2" -print0 | while IFS= read -r -d '' file; do
    echo "Processing file: $file"
    python ./scripts/oracle.py "$file" "$file.time" "$solvers_cfg_path" "$result_dir/$theory/bugs" $timeout $memout
done
