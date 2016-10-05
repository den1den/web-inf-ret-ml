#!/usr/bin/env bash
rm -r out
# cp elections-29-09.txt elections-29-09.txt.bak
# sed -i "s/}{/},\n{/g" elections-29-09.txt
mkdir out
cd out
split -l 400 ../elections-29-09.txt
ls -lah
echo File is split
python ../s.py