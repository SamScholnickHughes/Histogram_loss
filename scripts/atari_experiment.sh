#!/bin/bash
#SBATCH --job-name=atari
#SBATCH --output=%x-%j.out
#SBATCH --time=0-12:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=4000M
#SBATCH --gres=gpu:1
#SBATCH --mail-user=kluedema@ualberta.ca
#SBATCH --mail-type=ALL

PY_FILE=atari_main.py
BASE_DIR=~/scratch/Histogram_loss
ACTION_FILE=$BASE_DIR/atari_prediction/policies/PongNoFrameskip-v4.txt
RETURNS_FILE=returns_small.npy

module load python/3.10 scipy-stack
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install --no-index -r precompute_requirements.txt
pip install AutoROM-0.6.1-py3-none-any.whl AutoROM.accept-rom-license-0.6.1.tar.gz

python $BASE_DIR/$PY_FILE $ACTION_FILE $RETURNS_FILE