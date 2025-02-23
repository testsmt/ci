#! /bin/bash

if [ ! "$#" -eq 1 ]; then
    echo "Usage: $0 <theory>"
    exit 2
fi

result_dir=./results
db=$result_dir/$1.sqlite3

touch $db

sqlite3 $db "CREATE TABLE ExpResults(
            formula_idx INTEGER,
            solver_cfg TEXT NOT NULL,
            runtime DOUBLE NOT NULL,
            result TEXT NOT NULL
)"

i=0
for f in $(find $result_dir/$1/temp -name "*.time"); do
    if ! ((i % 100)); then
        echo $i,$f
    fi
    tail -n +4 "$f" > "$f.tmp"
    formula_idx=$(basename "$f" | cut -d'.' -f1)
    awk -v idx="$formula_idx" -F, 'BEGIN { OFS = "," } { if ($1 == "") $1 = idx; print }' "$f.tmp" > "$f.tmp.preprocessed"
    import_output=$(sqlite3 $db -echo -cmd ".mode csv" ".import $f.tmp.preprocessed ExpResults" 2>&1)

    if [[ $import_output == *"INSERT failed"* ]]; then
        echo "Error during import of $f.tmp.preprocessed:"
        echo "$import_output"
        echo "Contents of the file:"
        cat "$f.tmp.preprocessed"
    fi

    i=$((i+1))
done
