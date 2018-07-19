#!/bin/bash
#SBATCH -J deepAEtanh
#SBATCH -p normal_q
#SBATCH -n 1
##SBATCH --nodelist hu010
#SBATCH -t 2880:00
#SBATCH --mem=30G
#SBATCH --gres=gpu:pascal:1

module load anaconda2
module load cuda
source activate pytorch

RESULTDIR="/home/sathap1/workspace/bioFunctionPrediction/results/convAE/"
SCRIPT_ROOT="/home/sathap1/workspace/bioFunctionPrediction/src/"
cd $SCRIPT_ROOT

OUTDIR="${RESULTDIR}/model_tanh"
mkdir -p $OUTDIR

BATCHSIZE=32

python ${SCRIPT_ROOT}/cae.py --resources ${SCRIPT_ROOT}/../resources --outputdir $OUTDIR --trainsize $(( 5120000 / $BATCHSIZE )) --testsize $(( 2560000 / $BATCHSIZE )) --validationsize 100 --inputfile ${SCRIPT_ROOT}/../AllSeqsWithGO_expanded.tar --batchsize $BATCHSIZE

source deactivate
