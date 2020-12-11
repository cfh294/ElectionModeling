#!/bin/bash
# quick and dirty bash script to get all of the models and export their results
set -e 

currdir=$(dirname "0")
outdir=${currdir}/sample-output
for model in "HI" "GO" "PP" "PV" "GP" "VO" "ALL"; do
    python3 ${currdir}/classification.py -m "${model}" -c "ALL" -f ${outdir}/${model}.csv
done