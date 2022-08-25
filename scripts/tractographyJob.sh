#!/bin/bash

for subject in $(cat sublist.txt); do

        export subject
        echo "Submitting $subject"
        sbatch --job-name=$subject --output=/scratch/seharte_root/seharte99/shared_data/expl/job_output/tractography/$subject-%j_tracto.log tractographySbatch.sh

done