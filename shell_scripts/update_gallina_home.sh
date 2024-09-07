#!/bin/bash

source config.sh

rsync -av --progress $TMP_WORK_DIR/$PROG_DIR/frame_and_papers $GALLINA_HOME_DIR/frame_and_papers/
