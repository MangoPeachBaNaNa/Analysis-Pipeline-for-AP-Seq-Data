"""
:Author: Naici_G
:Date: 9 Nov 2025

:Description: Count peaks using featureCounts.
:Input: bam file.
:Output: txt files with counts for each bam file.
"""
# import modules
from ruffus import *
from cgatcore import pipeline as P
import glob
import sys
import os

@transform("*.bam",
       suffix(".bam"),
       ".txt")
def feature_count(infile, outfile):
    threads = 4
    statement = f"""featureCounts {infile} \
                -T {threads} \
                -a gencode.vM10.annotation.gtf.gz \
                -o {outfile} \
                -F GTF \
                -t transcript \
                -g gene_id \
                -p --countReadPairs \
                -O """
    P.run(statement, job_threads=threads,job_memory="16G")
@follows(feature_count)
def full():
    pass
def main(argv=None):
    if argv is None:
        argv = sys.argv
    P.main(argv)
if __name__ == "__main__":
    sys.exit(P.main(sys.argv))