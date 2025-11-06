"""
:Author: Naici_G
:Date: 3 Nov 2025
:Description:  Compute group matrix from log2-ratio bigwig files using computeMatrix from deepTools.

:Starting files: all *.log2ratio.bw files in the working directory.
:Output files: all_replicates_combined.matrix.gz, all_replicates_combined.tab, all_replicates_combined.bed
"""
# import modules
from ruffus import *
from cgatcore import pipeline as P
import glob
import sys
import os

# compute group matrix from log2-ratio bigwig files
INDIVIDUAL_BW_FILES = glob.glob("*_log2ratio.bw")
@merge(INDIVIDUAL_BW_FILES,
         ["all_replicates_combined.matrix.gz",
          "all_replicates_combined.tab",
          "all_replicates_combined.bed"])
def compute_group_matrix(infiles, outfiles):
    threads = 4
    input_strings = " ".join(infiles)
    outfile_matrix, outfile_name_matrix, outfile_sorted_regions = outfiles
    statement = f"""computeMatrix reference-point \
                --referencePoint TSS \
                -b 3000 -a 3000 \
                -R mm10_TSS.bed \
                -S {input_strings} \
                -o {outfile_matrix} \
                -p {threads} \
                --outFileNameMatrix {outfile_name_matrix} \
                --outFileSortedRegions {outfile_sorted_regions} """
    P.run(statement, job_memory="4G", job_threads=threads)

# plotProfile -m all_replicates_combined.matrix.gz -o all_replicates_profile.png --numPlotsPerRow 2
# plotProfile -m TSS.matrix.gz -o TSS.png --numPlotsPerRow 2 --colors black blue black blue black blue black blue
@follows(compute_group_matrix)
def full():
    pass
def main(argv=None):
    if argv is None:
        argv = sys.argv
    P.main(argv)
if __name__ == "__main__":
    sys.exit(P.main(sys.argv))