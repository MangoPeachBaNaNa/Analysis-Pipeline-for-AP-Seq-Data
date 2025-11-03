"""
:Author: Naici_G
:Date: 27 Oct 2025
:Description: Convert BAM files with marked duplicates to BigWig format, normalize using RPGC, then compute log2 ratio bigwig files for PD vs IN samples.

:Input files: All *.marked.sorted.bam files in the working directory.
:Output files: Corresponding .RPGC.bw and _log2ratio.bw files for each sample.
"""
# import modules
from ruffus import *
from cgatcore import pipeline as P
import glob
import sys
import os

# convert BAM to BigWig
@transform("*.marked.sorted.bam",
           suffix(".marked.sorted.bam"),
           ".RPGC.bw")
def bam_to_bigwig(infile, outfile):
    threads = 4
    statement = f'''bamCoverage -b {infile} \
                -o {outfile} \
                -of bigwig \
                --normalizeUsing RPGC \
                --effectiveGenomeSize 2652783500 \
                --binSize 10 \
                -p {threads} '''
    P.run(statement, job_memory="8G", job_threads=threads)

@follows(bam_to_bigwig)
@transform("*_PD.RPGC.bw",
           suffix("_PD.RPGC.bw"),
              "_log2ratio.bw")
def bw_to_log2ratio(infile, outfile):
    threads = 4
    PD_bw = infile
    IN_bw = infile.replace("_PD.RPGC.bw", "_IN.RPGC.bw")
    statement = f"""bigwigCompare -b1 {PD_bw} -b2 {IN_bw} \
                -o {outfile} \
                -of bigwig \
                -p {threads} \
                --operation log2 """
    P.run(statement, job_memory="4G", job_threads=threads)

# make individual matrix - it is not necesasary to run this if you only want the group matrix
"""
@follows(bw_to_log2ratio)
@transform("*_log2ratio.bw",
           suffix("_log2ratio.bw"),
           [".matrix.gz",
            ".tab",
            ".bed"])
def compute_matrix(infile, outfiles):
    threads = 4
    outfile_matrix, outfile_name_matrix, outfile_sorted_regions = outfiles
    statement = f'''computeMatrix reference-point \
                --referencePoint TSS \
                -b 3000 -a 3000 \
                -R mm10_TSS.bed \
                -S {infile} \
                -o {outfile_matrix} \
                -p {threads} \
                --outFileNameMatrix {outfile_name_matrix} \
                --outFileSortedRegions {outfile_sorted_regions} '''
    P.run(statement, job_memory="4G", job_threads=threads)
""" 
@follows(bw_to_log2ratio)
def full():
    pass
def main(argv=None):
    if argv is None:
        argv = sys.argv
    P.main(argv)
if __name__ == "__main__":
    sys.exit(P.main(sys.argv))