"""
:Author: Naici_G
:Date: 28 Oct 2025
:Description: Convert BAM files to BigWig files using bamcompare for PD vs IN samples, normalize using CPM, and compute log2 ratio.

:Input files: All *_PD.marked.sorted.bam and corresponding *_IN.marked.sorted.bam files in the working directory.
:Output files: Corresponding .PDvsIN.log2.bw files for each sample.
"""
# import modules
from ruffus import *
from cgatcore import pipeline as P
import glob
import sys
import os

PD_files = glob.glob("*_PD.marked.sorted.bam")
starting_files = [(file, file.replace("_PD.marked.sorted.bam", "_IN.marked.sorted.bam")) for file in PD_files]

# convert BAM to BigWig using bamcompare 
# normalize using CPM and log2 operation
@transform(starting_files,
           formatter("(?P<SAMPLE>.+)_PD.marked.sorted.bam"),
           f"{{SAMPLE[0]}}.PDvsIN.log2.bw")
def bam_to_bigwig(infile, outfile):
    threads = 4
    PD_file = infile[0]
    IN_file = infile[1]
    statement = f"""bamCompare -b1 {PD_file} -b2 {IN_file} \
                -o {outfile} \
                -of bigwig \
                -p {threads} \
                --scaleFactorsMethod None \
                --normalizeUsing CPM \
                --operation log2 \
                --effectiveGenomeSize 2652783500 \
                --binSize 10 """
    P.run(statement, job_memory="8G", job_threads=threads)

@follows(bam_to_bigwig)
def full():
    pass
def main(argv=None):
    if argv is None:
        argv = sys.argv
    P.main(argv)
if __name__ == "__main__":
    sys.exit(P.main(sys.argv))

