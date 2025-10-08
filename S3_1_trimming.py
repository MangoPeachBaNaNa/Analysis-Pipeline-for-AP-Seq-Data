"""
Updated on 2 Oct 2025 by Naici_G

:Description: Trim adapters from combined fastq files using Cutadapt & Trimmomatic.
"""
# import modules
from ruffus import *
from cgatcore import pipeline as P
import glob
import sys
import os

# Directories
data_merged_dir = "data_merged"
data_trimmed_dir = "data_trimmed_trimmomatic"

# Input files: paired-end FASTQ files
r1_files = sorted(glob.glob(os.path.join(data_merged_dir, "*_combined_1.fq.gz")))
starting_files = [(r1, r1.replace("_1.fq.gz","_2.fq.gz")) for r1 in r1_files]

# Check if paired files exist
print(f"Detected {len(starting_files)} paired FASTQ files.")
if len(starting_files) == 0:
    print("No input files found.")
    sys.exit(1)

# Trim adapters using fastp
@follows(mkdir(data_trimmed_dir))
@transform(starting_files,
           formatter(".+/(?P<SAMPLE>.+)_combined_1\.fq\.gz$"),
           [f"{data_trimmed_dir}/{{SAMPLE[0]}}_trimmed_1.fq.gz",
            f"{data_trimmed_dir}/{{SAMPLE[0]}}_trimmed_1_unpaired.fq.gz",
            f"{data_trimmed_dir}/{{SAMPLE[0]}}_trimmed_2.fq.gz",
            f"{data_trimmed_dir}/{{SAMPLE[0]}}_trimmed_2_unpaired.fq.gz"])

def trim_adapters_trimmomatic(infiles, outfiles):
    infile_r1, infile_r2 = infiles
    outfile_r1_paired, outfile_r1_unpaired, outfile_r2_paired, outfile_r2_unpaired = outfiles
    TRIMMOMATIC_HOME="/mnt/parscratch/users/bi1ng/trimmomatic/Trimmomatic-0.39"
    TRIMMOMATIC_JAR=f"{TRIMMOMATIC_HOME}/trimmomatic-0.39.jar"
    ADAPTERS_FILE = f"{TRIMMOMATIC_HOME}/adapters/TruSeq3-PE.fa"

    statement = f'''module load Java/8.362 && \
                java -jar {TRIMMOMATIC_JAR} \
                PE {infile_r1} {infile_r2} \
                {outfile_r1_paired} {outfile_r1_unpaired} \
                {outfile_r2_paired} {outfile_r2_unpaired} \
                ILLUMINACLIP:{ADAPTERS_FILE}:2:30:10:2:True LEADING:3 TRAILING:3 MINLEN:36'''
    P.run(statement, job_memory="16G", job_threads=2)

@follows(trim_adapters_trimmomatic)
def full():
    pass

def main(argv=None):
    if argv is None:
        argv = sys.argv
    P.main(argv)

if __name__ == "__main__":
    sys.exit(P.main(sys.argv))