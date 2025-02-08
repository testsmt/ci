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

# Iterate over each .smt2 file in the specified directory
find $result_dir/$theory/temp -name "*.smt2" -print0 | while IFS= read -r -d '' file; do
    echo "Processing file: $file"
    python ./scripts/oracle.py "$file" "$file.time" "$solvers_cfg_path" "$result_dir/$theory/bugs" $timeout $memout
done
