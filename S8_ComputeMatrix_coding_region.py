"""
:Author: Naici_G
:Date: 5 Nov 2025
:Description: Compute matrix for coding regions from log2-ratio bigwig files using computeMatrix from deepTools.

:Starting files: all *.log2ratio.bw files in the working directory.
:Output files: 
"""
# import modules
from ruffus import *
from cgatcore import pipeline as P
import glob
import sys
import os

INDIVIDUAL_BW_FILES = ["R1_WT_log2ratio.bw","R1_dTAG_log2ratio.bw",
                       "R2_WT_log2ratio.bw", "R2_dTAG_log2ratio.bw",
                       "R3_WT_log2ratio.bw", "R3_dTAG_log2ratio.bw",
                       "R4_WT_log2ratio.bw", "R4_dTAG_log2ratio.bw"]
# compute group matrix from log2-ratio bigwig files
@merge(INDIVIDUAL_BW_FILES,
         ["coding_region.matrix.gz",
          "coding_region.tab",
          "coding_region.bed"])
def compute_group_matrix_coding_region(infiles, outfiles):
    threads = 4
    input_strings = " ".join(infiles)
    outfile_matrix, outfile_name_matrix, outfile_sorted_regions = outfiles
    statement = f"""computeMatrix scale-regions \
                -R mm10_coding_region.bed \
                --regionBodyLength 1000 \
                --beforeRegionStartLength 1000 \
                --afterRegionStartLength 1000 \
                -S {input_strings} \
                -o {outfile_matrix} \
                -p {threads} \
                --outFileNameMatrix {outfile_name_matrix} \
                --outFileSortedRegions {outfile_sorted_regions} """
    P.run(statement, job_memory="4G", job_threads=threads)

@follows(compute_group_matrix_coding_region)
@transform("coding_region.matrix.gz",
           suffix(".matrix.gz"),
           ".png")
def plot_coding_profile(infile, outfile):
    statement = f"""plotProfile -m {infile} -o {outfile} \
                --numPlotsPerRow 2 --colors black blue black blue black blue black blue"""
    P.run(statement, job_memory="8G") #OOM when setting 4G
    
@follows(plot_coding_profile)
def full():
    pass
def main(argv=None):
    if argv is None:
        argv = sys.argv
    P.main(argv)
if __name__ == "__main__":
    sys.exit(P.main(sys.argv))