#!/bin/bash
#SBATCH --job-name=HLG-Aligned
#SBATCH --output=%x-%j.out
#SBATCH --time=0-12:00:00
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8000M
#SBATCH --mail-user=kluedema@ualberta.ca
#SBATCH --mail-type=ALL

DATA=megaage_asian.tgz
HYPERS=hlg_aligned_hypers.tgz
TUNER=keras_tuner-1.3.5-py3-none-any.whl
PY_FILE=Histogram_loss/HL_tuner.py

module load python/3.10 scipy-stack cuda cudnn 
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install --no-index -r requirements.txt
pip install --upgrade $TUNER

mkdir $SLURM_TMPDIR/data
tar -xzf $DATA -C $SLURM_TMPDIR/data
mkdir $SLURM_TMPDIR/hypers

python $PY_FILE $SLURM_TMPDIR

tar -czf $HYPERS -C $SLURM_TMPDIR hypers
