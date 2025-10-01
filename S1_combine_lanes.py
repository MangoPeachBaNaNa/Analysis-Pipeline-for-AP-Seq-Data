"""
:Author: Naici_G
:Date: 29 Sep 2025

:Description: Combine fastq files of AP-Seq reading from two lanes (L1 and L4) into single R1 and R2 files.
"""
# import modules
from ruffus import *
from cgatcore import pipeline as P
import glob
import sys
ALL_FILES = glob.glob("*.fq.gz")
REGEX_R1 = r"(R[1-4]_(?:dTAG|WT)_(?:IN|PD)_[A-Z0-9-]+)_.*_L\d+_1\.fq\.gz"
REGEX_R2 = r"(R[1-4]_(?:dTAG|WT)_(?:IN|PD)_[A-Z0-9-]+)_.*_L\d+_2\.fq\.gz"

# combine R1 files from multiple lanes

@collate(ALL_FILES,
         regex(REGEX_R1),
         r"merged_data/\1_combined_1.fq.gz")
def combine_R1(infiles, outfile):
    outdir = os.path.dirname(outfile)
    infiles_str = " ".join(infiles)
    statement = f'''mkdir -p {outdir} && zcat {infiles_str} | gzip > {outfile}'''
    P.run(statement, job_memory="8G", job_threads=1)

# combine R2 from multiple lanes
@collate(ALL_FILES,
         regex(REGEX_R2),
         r"merged_data/\1_combined_2.fq.gz")
def combine_R1(infiles, outfile):
    outdir = os.path.dirname(outfile)
    infiles_str = " ".join(infiles)
    statement = f'''mkdir -p {outdir} && zcat {infiles_str} | gzip > {outfile}'''
    P.run(statement, job_memory="8G", job_threads=1)

@follows([combine_R1, combine_R2])
def full():
    pass
def main(argv=None):
    if argv is None:
        argv = sys.argv
    P.main(argv)
if __name__ == "__main__":
    sys.exit(P.main(sys.argv))