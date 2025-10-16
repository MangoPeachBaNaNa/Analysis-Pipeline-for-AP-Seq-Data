"""
:Author: Naici_G
:Date: 16 Oct 2025

:Description: Index bam file, mark duplicates.
"""
# import modules
from ruffus import *
from cgatcore import pipeline as P
import glob
import sys
import os

@transform("*.bam",
           suffix(".bam"),
           ".sorted.bam")
def sort_bam(infile, outfile):
    threads = 4
    statement = f"""samtools sort -@ {threads} -m 4G -o {outfile} {infile}"""
    P.run(statement, job_threads=threads,job_memory="20G")

@transform(sort_bam,
           suffix(".sorted.bam"),
           ".sorted.bam.bai")
def index_bam(infile, outfile):
    statement = f"""module load SAMtools/1.16.1-GCC-11.3.0 &&
                   samtools index {infile}"""
    P.run(statement, job_memory="4G")

# mark duplicates using picard
@follows(sort_bam, index_bam)
@transform("*.sorted.bam",
           suffix(".sorted.bam"),
           [".marked.sorted.bam", 
            ".marked.sorted.bam.metrics.txt"])
def mark_duplicates(infile, outfiles):
    output_bam, metrics_file = outfiles
    threads = 4
    statement = f""" module load GATK/4.3.0.0-GCCcore-11.3.0-Java-11 &&
                    gatk MarkDuplicates
                       -I {infile}
                       -O {output_bam}
                       -M {metrics_file}
                       --CREATE_INDEX true
                       """
    P.run(statement, job_memory="4G", job_threads=threads)
    
@follows(mark_duplicates)
def full():
    pass
def main(argv=None):
    if argv is None:
        argv = sys.argv
    P.main(argv)
if __name__ == "__main__":
    sys.exit(P.main(sys.argv))