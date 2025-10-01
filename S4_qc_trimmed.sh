#!/bin/bash
#SBATCH --job-name=S2_qc
#SBATCH --time=4:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2

module load FastQC/0.12.1-Java-11
mkdir -p qc_reports_trimmed

fastqc *.fq.gz --threads 2 --outdir qc_reports_trimmed
echo "Report available at: qc_reports_trimmed"
#multiqc qc_reports -o qc_reports