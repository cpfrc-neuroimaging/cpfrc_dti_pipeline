#!/bin/bash

###SBATCH --job-name=$subject
#SBATCH --mail-user=user@example.com
#SBATCH --mail-type=END,FAIL

#SBATCH --account=FACULTY ACCOUNT
#SBATCH --partition=standard

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1

#SBATCH --cpus-per-task=8
#SBATCH --mem=16gb

#SBATCH --time=12:00:00
#SBATCH --export=ALL

#### End SBATCH preamble

module purge
module load fsl
module load freesurfer

my_job_header

# Set participant name
participant=$subject

# Create a local directory in which to work
TMPDIR=$(mktemp -d /tmp/USERNAME-recon-all.XXXXXXXXX)
cd $TMPDIR
mkdir BIDS


# Set the names of the fmriprep diretories.  NOTE, processed and work
# cannot be in the BIDS directory
SOURCE_DIR=/scratch/seharte_root/seharte99/shared_data/expl
BIDS_DIR=$PWD/BIDS
FREESURFER_WORK=$BIDS_DIR
SUBJECTS_DIR=$BIDS_DIR

# Get the needed BIDS data; print only the summary statistics from the copy
rsync -a --info=STATS /scratch/seharte_root/seharte99/shared_data/expl/dtiProc/$participant/t1spgr_208sl.nii ./BIDS

# Print some information about the run that might be useful
echo "#---------------------------------------------------------------------#"
echo "Running on           :  $(hostname -s)"
echo "Processor type       :  $(lscpu | grep 'Model name' | sed 's/[ \t][ ]*/ /g')"
echo "Assigned processors  :  $(cat /sys/fs/cgroup/cpuset/slurm/uid_${EUID}/job_${SLURM_JOBID}/cpuset.cpus)"
echo "Assigned memory nodes:  $(cat /sys/fs/cgroup/cpuset/slurm/uid_${EUID}/job_${SLURM_JOBID}/cpuset.mems)"
echo "======================================================================="
echo "/tmp space"
df -h /tmp
echo "======================================================================="
echo "Memory usage"
free
echo "#---------------------------------------------------------------------#"
echo



# Run it
source /etc/profile.d/http_proxy.sh

cd BIDS

### recon-all command

recon-all -i t1spgr_208sl.nii \
	-s sub-${participant}_T1w_recon -all

# Copy the results out for posterity
echo "Copying $OUTPUT_DIR/$participant to ${SOURCE_DIR}/recon-all"
mkdir -p ${SOURCE_DIR}/recon-all/${participant}
rsync -arv ${BIDS_DIR}/ ${SOURCE_DIR}/recon-all/${participant}/

# Change out of the $TMPDIR and remove it
cd
rm -rf $TMPDIR