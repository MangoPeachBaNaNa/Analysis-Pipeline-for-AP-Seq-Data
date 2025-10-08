"""
Updated on 7 Oct 2025 by Naici_G

:Description: Trim adapters from combined fastq files using Cutadapt.
"""
# import modules
from ruffus import *
from cgatcore import pipeline as P
import glob
import sys
import os

# Directories
data_merged_dir = "data_merged"
data_trimmed_dir = "data_trimmed_cutadapt"

# Input files: paired-end FASTQ files
r1_files = sorted(glob.glob(os.path.join(data_merged_dir, "*_combined_1.fq.gz")))
starting_files = [(r1, r1.replace("_1.fq.gz","_2.fq.gz")) for r1 in r1_files]

# Check if paired files exist
print(f"Detected {len(starting_files)} paired FASTQ files.")
if len(starting_files) == 0:
    print("No input files found.")
    sys.exit(1)

# Trim adapters using cutadapt
@follows(mkdir(data_trimmed_dir))
@transform(starting_files,
           formatter(".+/(?P<SAMPLE>.+)_combined_1\.fq\.gz$"),
           [f"{data_trimmed_dir}/{{SAMPLE[0]}}_trimmed_1.fq.gz",
            f"{data_trimmed_dir}/{{SAMPLE[0]}}_trimmed_2.fq.gz"])

def trim_adapters_cutadapt(infiles, outfiles):
    infile_r1, infile_r2 = infiles
    outfile_r1, outfile_r2 = outfiles
    statement = f"""cutadapt \
                -a "AGATCGGAAGAGC" \
                -A "AGATCGGAAGAGC" \
                -q 3,3 \
                -m 36 \
                -j 4 \
                -o {outfile_r1} -p {outfile_r2} \
                {infile_r1} {infile_r2}"""
    P.run(statement, job_memory="16G", job_threads=4)
@follows(trim_adapters_cutadapt)

def full():
    pass
def main(argv=None):
    if argv is None:
        argv = sys.argv
    P.main(argv)
if __name__ == "__main__":
    sys.exit(P.main(sys.argv))