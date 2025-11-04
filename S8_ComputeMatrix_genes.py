"""
:Author: Naici_G
:Date: 3 Nov 2025
:Description: Compute group matrix from log2-ratio bigwig files for specific genes (i.e.,FOS) using computeMatrix from deepTools.

:Starting files: all *.log2ratio.bw files in the working directory.
:Output files: {gene}.matrix.gz, {gene}.tab, {gene}.bed
"""
from ruffus import *
from cgatcore import pipeline as P
import glob
import sys
import os

# There are three specific genes we are interested in
# FOS, SRF & CCN2
GENE = "FOS"
INDIVIDUAL_BW_FILES = glob.glob("*_log2ratio.bw")
# shouldn't use collate but merge here
@merge(INDIVIDUAL_BW_FILES,
         [f"{GENE}.matrix.gz",
          f"{GENE}.tab",
          f"{GENE}.bed"])

# gene is not the same with TSS - shouldn't be using reference-point center?
def compute_group_matrix_gene_FOS(infiles, outfiles):
    threads = 4
    input_strings = " ".join(infiles)
    outfile_matrix, outfile_name_matrix, outfile_sorted_regions = outfiles
    statement = f"""computeMatrix scale-regions \
                -R FOS_gene.bed \
                --regionBodyLength 1000 \
                --beforeRegionStartLength 1000 \
                --afterRegionStartLength 1000 \
                -S {input_strings} \
                -o {outfile_matrix} \
                -p {threads} \
                --outFileNameMatrix {outfile_name_matrix} \
                --outFileSortedRegions {outfile_sorted_regions} """
    P.run(statement, job_memory="4G", job_threads=threads)

@follows(compute_group_matrix_gene_FOS)
def full():
    pass
def main(argv=None):
    if argv is None:
        argv = sys.argv
    P.main(argv)
if __name__ == "__main__":
    sys.exit(P.main(sys.argv))