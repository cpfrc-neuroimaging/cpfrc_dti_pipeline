#!/bin/bash

###SBATCH --job-name=$subject
#SBATCH --mail-user=dasay@med.umich.edu
#SBATCH --mail-type=END,FAIL

#SBATCH --account=kboehnke99
#SBATCH --partition=standard

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1

#SBATCH --cpus-per-task=8
#SBATCH --mem=16gb

#SBATCH --time=5:00:00
#SBATCH --export=ALL

#### End SBATCH preamble

module purge
module load mrtrix

my_job_header

# Set participant name
participant=$subject

# Create a local directory in which to work
TMPDIR=$(mktemp -d /tmp/dasay-tractography.XXXXXXXXX)
cd $TMPDIR
mkdir BIDS

# Set the names of the tractography diretories.
SOURCE_DIR=/scratch/seharte_root/seharte99/shared_data/expl
BIDS_DIR=$PWD/BIDS

# Get the needed BIDS data; print only the summary statistics from the copy
rsync -a --info=STATS /scratch/seharte_root/seharte99/shared_data/expl/dtiProc/$participant/5tt_coreg.mif ./BIDS
rsync -a --info=STATS /scratch/seharte_root/seharte99/shared_data/expl/dtiProc/$participant/gmwmSeed_coreg.mif ./BIDS
rsync -a --info=STATS /scratch/seharte_root/seharte99/shared_data/expl/dtiProc/$participant/wmfod_norm.mif ./BIDS
# only do this if first command was run previously
#rsync -a --info=STATS /scratch/seharte_root/seharte99/shared_data/expl/dtiProc/$participant/tracks_10M.tck ./BIDS

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

### tractography command

tckgen -act 5tt_coreg.mif \
	-backtrack -seed_gmwmi gmwmSeed_coreg.mif \
	-nthreads 8 -maxlength 250 -cutoff 0.06 \
	-select 10000000 wmfod_norm.mif tracks_10M.tck

### overfitting command

tcksift2 -act 5tt_coreg.mif \
	-out_mu sift_mu.txt -out_coeffs sift_coeffs.txt \
	-nthreads 8 tracks_10M.tck wmfod_norm.mif sift_1M.txt

# Copy the results out for posterity
echo "Copying $OUTPUT_DIR/$participant to ${SOURCE_DIR}/tractography"
mkdir -p ${SOURCE_DIR}/tractography/${participant}
rsync -arv ${BIDS_DIR}/ ${SOURCE_DIR}/tractography/${participant}

# Change out of the $TMPDIR and remove it
cd
rm -rf $TMPDIR