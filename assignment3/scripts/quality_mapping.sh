#!/usr/bin/env bash
set -e

SAMPLE=ERR16175435
READS=data/raw/ERR16175435.fastq.gz
REF_GZ=data/ref/GCF_000005845.2_ASM584v2_genomic.fna.gz
OUT=results/ERR16175435
THREADS=4
MINIMAP2=tools/minimap2/minimap2

mkdir -p "$OUT/fastqc"
mkdir -p "$OUT/logs"
mkdir -p "$OUT/work"
rm -f "$OUT/flagstat.txt"
rm -f "$OUT/mapping_status.txt"
rm -f "$OUT/pipeline_finished.txt"
rm -f "$OUT/work/$SAMPLE.vcf"

fastqc --threads "$THREADS" --outdir "$OUT/fastqc" "$READS"

gzip -dc "$REF_GZ" > "$OUT/work/reference.fna"

"$MINIMAP2" -d "$OUT/work/reference.mmi" "$OUT/work/reference.fna"

"$MINIMAP2" -a "$OUT/work/reference.mmi" "$READS" > "$OUT/work/$SAMPLE.sam"

samtools view -@ "$THREADS" -bS "$OUT/work/$SAMPLE.sam" > "$OUT/work/$SAMPLE.bam"

samtools flagstat "$OUT/work/$SAMPLE.bam" > "$OUT/flagstat.txt"

python3 scripts/parse_flagstat.py

if grep -q "status=OK" "$OUT/mapping_status.txt"; then
  echo "OK"
  samtools sort -@ "$THREADS" -o "$OUT/work/$SAMPLE.sorted.bam" "$OUT/work/$SAMPLE.bam"
  samtools index "$OUT/work/$SAMPLE.sorted.bam"
  samtools faidx "$OUT/work/reference.fna"
  freebayes -f "$OUT/work/reference.fna" "$OUT/work/$SAMPLE.sorted.bam" > "$OUT/work/$SAMPLE.vcf"
  echo "Finished" > "$OUT/pipeline_finished.txt"
else
  echo "not OK"
fi
