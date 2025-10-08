"""
Updated on 7 Oct 2025 by Naici_G

:Description: Trim adapters from combined fastq files using Cutadapt & trimmomatic & fastp.
"""
# import modules
from ruffus import *
from cgatcore import pipeline as P
import glob
import sys
import os

# Directories
data_merged_dir = "data_merged"
data_trimmed_dir = "data_trimmed_cutadapt_trimmomatic"

# Input files: paired-end FASTQ files
r1_files = sorted(glob.glob(os.path.join(data_merged_dir, "*_combined_1.fq.gz")))
starting_files = [(r1, r1.replace("_1.fq.gz","_2.fq.gz")) for r1 in r1_files]

# Check if paired files exist
print(f"Detected {len(starting_files)} paired FASTQ files.")
if len(starting_files) == 0:
    print("No input files found.")
    sys.exit(1)

# Trim adapters using cutadapt
@follows(mkdir(data_trimmed_dir))
@transform(starting_files,
           formatter(".+/(?P<SAMPLE>.+)_combined_1\.fq\.gz$"),
           [f"{data_trimmed_dir}/{{SAMPLE[0]}}_trimmed_c_1.fq.gz",
            f"{data_trimmed_dir}/{{SAMPLE[0]}}_trimmed_c_2.fq.gz"])
def trim_cutadapt(infiles, outfiles):
    infile_r1, infile_r2 = infiles
    outfile_r1, outfile_r2 = outfiles
    statement = f"""cutadapt \
                -a "AGATCGGAAGAGC" \
                -A "AGATCGGAAGAGC" \
                -q 3,3 \
                -m 36 \
                -j 2 \
                -o {outfile_r1} -p {outfile_r2} \
                {infile_r1} {infile_r2}"""
    P.run(statement, job_memory="16G", job_threads=2)

@transform(trim_cutadapt,
           regex(r".+/(.+)_trimmed_c_1\.fq\.gz$"),
           [rf"{data_trimmed_dir}/\1_trimmed_c_t.fq.gz",
            rf"{data_trimmed_dir}/\1_trimmed_c_t_1_unpaired.fq.gz",
            rf"{data_trimmed_dir}/\1_trimmed_c_t_2.fq.gz",
            rf"{data_trimmed_dir}/\1_trimmed_c_t_2_unpaired.fq.gz"])
def trim_trimmomatic(infiles, outfiles):
    infile_r1, infile_r2 = infiles
    outfile_r1_paired, outfile_r1_unpaired, outfile_r2_paired, outfile_r2_unpaired = outfiles
    TRIMMOMATIC_HOME="/mnt/parscratch/users/bi1ng/trimmomatic/Trimmomatic-0.39"
    TRIMMOMATIC_JAR=f"{TRIMMOMATIC_HOME}/trimmomatic-0.39.jar"
    ADAPTERS_FILE = f"{TRIMMOMATIC_HOME}/adapters/TruSeq3-PE.fa"

    statement = f'''module load Java/8.362 && \
                java -jar {TRIMMOMATIC_JAR} \
                PE {infile_r1} {infile_r2} \
                {outfile_r1_paired} {outfile_r1_unpaired} \
                {outfile_r2_paired} {outfile_r2_unpaired} \
                ILLUMINACLIP:{ADAPTERS_FILE}:2:30:10:2:True LEADING:3 TRAILING:3 MINLEN:36'''
    P.run(statement, job_memory="16G", job_threads=2)

@transform(trim_trimmomatic,
              regex(r".+/(.+)_trimmed_c_t_1\.fq\.gz$"),
              [rf"{data_trimmed_dir}/\1_clean_1.fq.gz",
                rf"{data_trimmed_dir}/\1_clean_2.fq.gz"])
def trim_fastp(infiles, outfiles):
    infile_r1, infile_r2 = infiles
    outfile_r1, outfile_r2 = outfiles
    sample_prefix = os.path.basename(infile_r1).replace("_trimmed_c_t_1.fq.gz", "")
    statement = f"""module load fastp/0.23.4-GCC-12.3.0 &&
                fastp \
                -i {infile_r1} -I {infile_r2} \
                -o {outfile_r1} -O {outfile_r2} \
                --trim_poly_g --trim_poly_x \
                --detect_adapter_for_pe \
                --thread 4 \
                --json {data_trimmed_dir}/{sample_prefix}_fastp.json \
                --html {data_trimmed_dir}/{sample_prefix}_fastp.html \
                """
    P.run(statement, job_memory="16G", job_threads=4)   

@follows(trim_fastp)
def full():
    pass
def main(argv=None):
    if argv is None:
        argv = sys.argv
    P.main(argv)
if __name__ == "__main__":
    sys.exit(P.main(sys.argv))