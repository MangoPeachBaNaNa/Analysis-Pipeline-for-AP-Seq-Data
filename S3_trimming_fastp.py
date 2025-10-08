"""
:Author: Naici_G
:Date: 1 Oct 2025

:Description: Trim adapters from combined fastq files using fastp.
"""
# import modules
from ruffus import *
from cgatcore import pipeline as P
import glob
import sys
import os

# Directories
data_merged_dir = "data_merged"
data_trimmed_dir = "data_trimmed"

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
            f"{data_trimmed_dir}/{{SAMPLE[0]}}_trimmed_2.fq.gz"])
def trim_adapters(infiles, outfiles):
    infile_r1, infile_r2 = infiles
    outfile_r1, outfile_r2 = outfiles
    sample_prefix = os.path.basename(infile_r1).replace("_combined_1.fq.gz", "")
    statement = f'''module load fastp/0.23.4-GCC-12.3.0 &&
                fastp \
                -i {infile_r1} -I {infile_r2} \
                -o {outfile_r1} -O {outfile_r2} \
                --detect_adapter_for_pe \
                --thread 4 \
                --json {data_trimmed_dir}/{sample_prefix}_fastp.json \
                --html {data_trimmed_dir}/{sample_prefix}_fastp.html \
                '''
    P.run(statement, job_memory="16G", job_threads=4)

@follows(trim_adapters)
def full():
    pass
def main(argv=None):
    if argv is None:
        argv = sys.argv
    P.main(argv)
if __name__ == "__main__":
    sys.exit(P.main(sys.argv))