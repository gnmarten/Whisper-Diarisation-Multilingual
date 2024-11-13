#!/bin/bash
#PBS -N x_jobname
#PBS -m ae
#PBS -l walltime=2:59:00
#PBS -l nodes=1:ppn=12:gpus=1
#PBS -l mem=50gb

# Load required modules
#module purge
module load foss/2023a
module load CUDA/12.1.1
module load cuDNN/8.9.2.26-CUDA-12.1.1
module load Python/3.11.3-GCCcore-12.3.0
module load PyTorch/2.1.2-foss-2023a
module load PyTorch-Lightning/2.1.3-foss-2023a
module load Transformers/4.39.3-gfbf-2023a

# Setup cache and install directories on scratch
export XDG_CACHE_HOME=/kyukon/scratch/gent/427/vsc42730/cache
export PIP_CACHE_DIR=/kyukon/scratch/gent/427/vsc42730/pip_cache
export PYTHONUSERBASE=/kyukon/scratch/gent/427/vsc42730/python_packages
export PATH=$PYTHONUSERBASE/bin:$PATH
# Add the path to your local PyTorch CUDA libraries
export LD_LIBRARY_PATH=/kyukon/scratch/gent/427/vsc42730/python_packages/lib/python3.11/site-packages/torch/lib:$LD_LIBRARY_PATH

# Also add the CUDA libraries from the module
export LD_LIBRARY_PATH=/apps/gent/RHEL8/zen3-ampere-ib/software/CUDA/12.1.1/lib64:$LD_LIBRARY_PATH
export PYTHONPATH=/kyukon/scratch/gent/427/vsc42730/python_packages/lib/python3.11/site-packages:$PYTHONPATH

# Upgrade pip and resolve dependency issues
pip install --user --upgrade pip
pip install --user mlxtend numba whisperx 
#pip install --user pyannote.audio --extra-index-url https://download.pytorch.org/whl/cu121
pip install --user pyannote.audio --extra-index-url https://download.pytorch.org/whl/cu121
#pip uninstall -y safetensors
#pip install --user safetensors
module list | grep cuda
module show CUDA/12.1.1

# Run the script
cd $VSC_HOME
python diarisation.py

exit 0
