#!/bin/bash
#SBATCH --job-name=Parallel
#SBATCH --output=%x-%j.out
#SBATCH --time=1-00:00:00
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --cpus-per-task=24
#SBATCH --mem=128000M
#SBATCH --gpus-per-node=p100:4
#SBATCH --mail-user=kluedema@ualberta.ca
#SBATCH --mail-type=ALL

GAMES_FILE=games.txt
BASE_DIR=~/scratch

POLICY_DIR=$SLURM_TMPDIR/data/policies
DATA=$BASE_DIR/data/policies.zip

module load python/3.10 scipy-stack cuda cudnn
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install --no-index -r atari_requirements.txt
pip install AutoROM-0.6.1-py3-none-any.whl AutoROM.accept-rom-license-0.6.1.tar.gz ../keras_tuner-1.3.5-py3-none-any.whl

mkdir $SLURM_TMPDIR/data
unzip $DATA -d $SLURM_TMPDIR/data

parallel 'CUDA_VISIBLE_DEVICES=$((({%} - 1) % 4)) source run_game.sh {} &> {}.out' < $GAMES_FILE
