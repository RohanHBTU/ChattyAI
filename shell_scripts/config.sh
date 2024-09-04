#!/bin/bash

# Customize these variables
USERID="rks110"
NODE="gpu"

GALLINA_HOME_DIR="/mnt/rds/redhen/gallina/home/$USERID"
PROG_DIR="frame_chat"
TMP_WORK_DIR="/scratch/users/$USERID"
FRAME_DIR="/mnt/rds/redhen/gallina/projects/ChattyAI/FramesConstructions/fndata-1.7/frame"

module load Python/3.11.3
module load PyTorch/2.1.2-foss-2023a-CUDA-12.1.1
module load PyYAML/6.0-GCCcore-12.3.0

