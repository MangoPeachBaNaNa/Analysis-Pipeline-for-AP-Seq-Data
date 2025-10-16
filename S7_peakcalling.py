"""
:Author: Naici_G
:Date: 16 Oct 2025

:Description: Call peaks.
"""
# import modules
from ruffus import *
from cgatcore import pipeline as P
import glob
import sys
import os

PD_FILES = glob.glob( "*_PD.marked.sorted.bam")
starting_files = [(pd_file, pd_file.replace("_PD.marked.sorted.bam", "_IN.marked.sorted.bam")) for pd_file in PD_FILES]

@transform(starting_files,
              regex(r"(?P<SAMPLE>.+)_PD\.marked\.sorted\.bam"),
              r"peaks_inclusive/\1")           
# call peaks, include duplicated areas
def call_peaks_inclusive(infiles, outdir):
    threads = 4
    pull_down, input_control = infiles
    os.makedirs(outdir, exist_ok=True)
    sample_name = os.path.basename(pull_down).replace("_PD.marked.sorted.bam", "")
    statement = f""" macs2 callpeak \
                -t {pull_down} \
                -c {input_control} \
                -f BAMPE \
                -g mm \
                -n {sample_name} \
                --outdir {outdir} \
                --keep-dup all""" 
    P.run(statement, job_memory="4G", job_threads=threads)

@transform(starting_files,
              regex(r"(?P<SAMPLE>.+)_PD\.marked\.sorted\.bam"),
              r"peaks_exclusive/\1")     
# call peaks, exclude duplicated areas
def call_peaks_exclusive(infiles, outdir):
    threads = 4
    pull_down, input_control = infiles
    os.makedirs(outdir, exist_ok=True)
    sample_name = os.path.basename(pull_down).replace("_PD.marked.sorted.bam", "")
    statement = f""" macs2 callpeak \
                -t {pull_down} \
                -c {input_control} \
                -f BAMPE \
                -g mm \
                -n {sample_name} \
                --outdir {outdir} \
                --keep-dup auto""" 
    P.run(statement, job_memory="4G", job_threads=threads)

@follows(call_peaks_inclusive, call_peaks_exclusive)
def full():
    pass
def main(argv=None):
    if argv is None:
        argv = sys.argv
    P.main(argv)
if __name__ == "__main__":
    sys.exit(P.main(sys.argv))