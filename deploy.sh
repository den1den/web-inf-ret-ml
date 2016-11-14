#!/bin/sh
# -*- coding: utf-8 -*-
echo "Updating web-inf-ret-ml"
cd /home/webinfret/web-inf-ret-ml
git status
git pull
echo "Updating web-inf-retrieval"
cd /home/webinfret/web-inf-retrieval
git status
git pull

supervisorctl restart webinfret
