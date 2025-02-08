#!/bin/bash

if [ ! "$#" -eq 5 ]; then
    echo "Usage: $0 <theory> <num_tests> <solvers_cfg_path>"
    exit 2
fi

theory=$1
num_tests=$2
timeout=8.0
memout=1048576
solvers_cfg_path=$5
num_cores=4
result_dir="./results"

find $result_dir/temp-$theory -name "*.smt2" -print0 | \
parallel -0 -j${num_cores} --eta --progress --bar ./oracle {} {}.time "$solvers_cfg_path" $result_dir/bugs-$theory $timeout $memout