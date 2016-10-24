#!/usr/bin/env bash
cd /home/dennis/tmp2/tweet/elections-04-10-raw
rm -r out
cp 20161003___0.json 20161004___0.json.bak
sed -i "s/}{/},\n{/g" 20161004___0.json
mkdir out
cd out
split -l 400 ../20161004___0.json
ls -lah
echo File is split
python /home/dennis/repos/web-inf-ret-ml/split_files_script/s.py
