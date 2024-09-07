#!/bin/bash

source config.sh

cd $GALLINA_HOME_DIR/
git pull origin main

if [ ! -d $TMP_WORK_DIR ]; then
    mkdir $TMP_WORK_DIR
fi

rsync -av --progress $GALLINA_HOME_DIR/frame_and_papers $TMP_WORK_DIR/$PROG_DIR/

cd $TMP_WORK_DIR/$PROG_DIR
source .venv/bin/activate
pip install -r requirements.txt
deactivate

