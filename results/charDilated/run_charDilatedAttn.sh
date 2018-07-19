#!/bin/bash
# Resources can be requested by specifying the number of nodes, cores, memory, GPUs, etc
# Examples:
#   Request 2 nodes with 24 cores each
#   #PBS -l nodes=1:ppn=24
#   Request 4 cores (on any number of nodes)
#   #PBS -l procs=4
#   Request 12 cores with 20gb memory per core
#   #PBS -l procs=12,pmem=20gb
#   Request 2 nodes with 24 cores each and 20gb memory per core (will give two 512gb nodes)
#   #PBS -l nodes=2:ppn=24,pmem=20gb
#   Request 2 nodes with 24 cores per node and 1 gpu per node
#   #PBS -l nodes=2:ppn=24:gpus=1
#   Request 2 cores with 1 gpu each
#   #PBS -l procs=2,gpus=1
#   #PBS -l nodes=1:ppn=24

#PBS -l nodes=1:gpus=1

#PBS -l walltime=06:00:00

#### Queue ####
# Queue name. NewRiver has seven queues:
#   normal_q        for production jobs on all Haswell nodes (nr003-nr126)
#   largemem_q      for jobs on the two 3TB, 60-core Ivy Bridge servers (nr001-nr002)
#   dev_q           for development/debugging jobs on Haswell nodes. These jobs must be short but can be large.
#   vis_q           for visualization jobs on K80 GPU nodes (nr019-nr027). These jobs must be both short and small.
#   open_q          for jobs not requiring an allocation. These jobs must be both short and small.
#   p100_normal_q   for production jobs on P100 GPU nodes
#   p100_dev_q      for development/debugging jobs on P100 GPU nodes. These jobs must be short but can be large.
# For more on queues as policies, see http://www.arc.vt.edu/newriver#policy

#PBS -q p100_normal_q

#### Account ####
# This determines which allocation this job's CPU hours are billed to.
# Replace "youraccount" below with the name of your allocation account.
# If you are a student, you will need to get this from your advisor.
# For more on allocations, go here: http://www.arc.vt.edu/allocations

#PBS -A fungcat1

# Access group. Do not change this line.

#PBS -W group_list=newriver

# Uncomment and add your email address to get an email when your job starts, completes, or aborts

#PBS -M sathap1@vt.edu

# #PBS -m bea

# Change to the directory from which the job was submitted

#PBS -e /home/sathap1/workspace/bioFunctionPrediction/results/charDilated/error_bp.log
#PBS -o /home/sathap1/workspace/bioFunctionPrediction/results/charDilated/output_bp.log

OUTDIR="/home/sathap1/workspace/bioFunctionPrediction/results/charDilated/models/bp/"
SCRIPT_ROOT="/home/sathap1/workspace/bioFunctionPrediction/src/"

mkdir -p $OUTDIR
cd $SCRIPT_ROOT
module purge
module load Anaconda
module load cuda/8.0.44
module load cudnn/6.0

source activate /home/sathap1/newriver_local/venvs/tfgpu

python ${SCRIPT_ROOT}/char_run.py --function bp --resources ${SCRIPT_ROOT}/../resources --outputdir $OUTDIR --trainsize 6000 --testsize 6000 --validationsize 100 --inputfile ${SCRIPT_ROOT}/../AllSeqsWithGO_expanded.tar --batchsize 32 --pretrained ${SCRIPT_ROOT}/../resources/protVec_100d_3grams.csv --inputfile ../AllSeqsWithGO_expanded.tar --predict ${OUTDIR}/savedmodels_charDilatedAttn_1527438389

source deactivate
