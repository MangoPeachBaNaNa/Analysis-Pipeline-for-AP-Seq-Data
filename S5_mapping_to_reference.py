"""
:Author: Naici_G
:Date: 9 Oct 2025

:Description: Mapping.
"""

from ruffus import *
from cgatcore import pipeline as P
import glob
import os
import sys


r1_files = glob.glob("*_1.fq.gz")
starting_files = [(r1, r1.replace("_1.fq.gz", "_2.fq.gz")) for r1 in r1_files]

reference_dir = "reference"

print(f"Detected {len(starting_files)} paired FASTQ files.")
if len(starting_files) == 0:
    print("No input files found.")
    sys.exit(1)

@transform(starting_files,
        suffix("_1.fq.gz"),
        ".bam")
def map_sequence(input_files, output_file):
    r1 = input_files[0]
    r2 = input_files[1]
    threads = 4
    job_options = "-t 96:00:00"
    sample_name = os.path.basename(r1).replace("-1A_final_1.fq.gz", "")
    statement = f"""module load samtools &&
                bwa mem -t {threads} -M {reference_dir}/mm10_all {r1} {r2} | \
                samtools view -bS -F 256 -q 30 > {output_file} """
    


    print(f"Running BWA mapping for {sample_name}")
    P.run(statement, job_memory="8G", job_threads=threads)

@follows(map_sequence)
def full():
    pass
def main(argv=None):
    if argv is None:
        argv = sys.argv
    P.main(argv)
if __name__ == "__main__":
    sys.exit(P.main(sys.argv))