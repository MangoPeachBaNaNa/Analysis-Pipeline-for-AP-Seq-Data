"""
:Author: Naici_G
:Date: 5 Nov 2025
:Description:  Compute group matrix for enhancer regions from log2-ratio bigwig files using computeMatrix from deepTools.

:Starting files: all *.log2ratio.bw files in the working directory.
:Output files: enhancers.matrix.gz, enhancers.tab, enhancers.bed
"""
# import modules
from ruffus import *
from cgatcore import pipeline as P
import glob
import sys
import os

# compute group matrix from log2-ratio bigwig files
# INDIVIDUAL_BW_FILES = glob.glob("*_log2ratio.bw")
INDIVIDUAL_BW_FILES = ["R1_WT_log2ratio.bw","R1_dTAG_log2ratio.bw",
                       "R2_WT_log2ratio.bw", "R2_dTAG_log2ratio.bw",
                       "R3_WT_log2ratio.bw", "R3_dTAG_log2ratio.bw",
                       "R4_WT_log2ratio.bw", "R4_dTAG_log2ratio.bw"]
@merge(INDIVIDUAL_BW_FILES,
         ["enhancers.matrix.gz",
          "enhancers.tab",
          "enhancers.bed"])
def compute_group_matrix(infiles, outfiles):
    threads = 4
    input_strings = " ".join(infiles)
    outfile_matrix, outfile_name_matrix, outfile_sorted_regions = outfiles
    statement = f"""computeMatrix scale-regions \
                --regionBodyLength 200 \
                --beforeRegionStartLength 500 \
                --afterRegionStartLength 500 \
                --binSize 10 \
                --startLabel Enhancer_Start \
                --endLabel Enhancer_End \
                -R mm10_enhancer_neuron_cortical_E16.bed \
                -S {input_strings} \
                -o {outfile_matrix} \
                -p {threads} \
                --outFileNameMatrix {outfile_name_matrix} \
                --outFileSortedRegions {outfile_sorted_regions} """
    P.run(statement, job_memory="4G", job_threads=threads)

@follows(compute_group_matrix)
@transform("enhancers.matrix.gz",
           suffix(".matrix.gz"),
           ".png")
def plot_enhancer_profile(infile, outfile):
    statement = f"""plotProfile -m {infile} -o {outfile} \
                --numPlotsPerRow 2 --colors black blue black blue black blue black blue \
                --startLabel Enhancer_Start --endLabel Enhancer_End """
    P.run(statement, job_memory="4G", job_threads=1)
@follows(plot_enhancer_profile)
def full():
    pass
def main(argv=None):
    if argv is None:
        argv = sys.argv
    P.main(argv)
if __name__ == "__main__":
    sys.exit(P.main(sys.argv))