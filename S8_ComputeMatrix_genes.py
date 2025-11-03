"""
:Author: Naici_G
:Date: 27 Oct 2025
:Description: Convert BAM files with marked duplicates to BigWig format.
"""
from ruffus import *
from cgatcore import pipeline as P
import glob
import sys
import os

GENE = "FOS"
INDIVIDUAL_BW_FILES = glob.glob("*.log2ratio.bw")
@collate(INDIVIDUAL_BW_FILES,
         regex(r".*"), 
         [f"{GENE}.matrix.gz",
          f"{GENE}.tab",
          "FOS_gene.bed"])
def compute_group_matrix_gene_FOS(infiles, outfiles):
    threads = 4
    input_strings = " ".join(infiles)
    outfile_matrix, outfile_name_matrix, outfile_sorted_regions = outfiles
    statement = f"""computeMatrix reference-point \
                --referencePoint center \
                -b 5000 -a 5000 \
                -R FOS_gene.bed \
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