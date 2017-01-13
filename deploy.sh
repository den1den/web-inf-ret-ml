#!/bin/sh
# -*- coding: utf-8 -*-
echo "Updating: web-inf-ret-ml"
cd /home/webinfret/web-inf-ret-ml
git status
git pull
echo ""
echo "Updating: web-inf-retrieval"
cd /home/webinfret/web-inf-retrieval
git status
git pull
echo ""
echo "Updating: webinfret"
cd /home/webinfret/webinfret
git status
git pull
echo ""
echo "Updating: IndexBuilder"
cd /home/webinfret/IndexBuilder
git status
git pull
cp src/main/java/indexing/Config.java.server.txt src/main/java/indexing/Config.java
./restart-glashfish.sh
