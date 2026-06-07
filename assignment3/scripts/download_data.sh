#!/usr/bin/env bash
set -e

mkdir -p data/raw
mkdir -p data/ref
mkdir -p results/ERR16175435/logs

wget -O data/raw/ERR16175435.fastq.gz "https://trace.ncbi.nlm.nih.gov/Traces/sra-reads-be/fastq?acc=ERR16175435"

wget -O data/ref/GCF_000005845.2_ASM584v2_genomic.fna.gz "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/005/845/GCF_000005845.2_ASM584v2/GCF_000005845.2_ASM584v2_genomic.fna.gz"

echo "Downloaded input files"
