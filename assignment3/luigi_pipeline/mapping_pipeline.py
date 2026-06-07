#!/usr/bin/env python3
from __future__ import annotations

import gzip
import re
import shutil
import subprocess
from pathlib import Path

import luigi


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = "ERR16175435"
THREADS = "4"
THRESHOLD = 90.0
READS = ROOT / "data" / "raw" / "ERR16175435.fastq.gz"
REF_GZ = ROOT / "data" / "ref" / "GCF_000005845.2_ASM584v2_genomic.fna.gz"
OUT = ROOT / "results" / SAMPLE / "luigi"
WORK = OUT / "work"
LOG = OUT / "logs" / "pipeline.log"
MINIMAP2 = ROOT / "tools" / "minimap2" / "minimap2"


def run(command: list[str], stdout: Path | None = None) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as log:
        if stdout:
            stdout.parent.mkdir(parents=True, exist_ok=True)
            with stdout.open("w", encoding="utf-8") as out:
                subprocess.run(command, check=True, text=True, stdout=out, stderr=log)
        else:
            subprocess.run(command, check=True, text=True, stdout=log, stderr=log)


class InputFiles(luigi.ExternalTask):
    def output(self):
        return {
            "reads": luigi.LocalTarget(str(READS)),
            "ref": luigi.LocalTarget(str(REF_GZ)),
        }


class FastQCReads(luigi.Task):
    def requires(self):
        return InputFiles()

    def output(self):
        return luigi.LocalTarget(str(OUT / "fastqc" / "ERR16175435_fastqc.html"))

    def run(self):
        (OUT / "fastqc").mkdir(parents=True, exist_ok=True)
        run(["fastqc", "--threads", THREADS, "--outdir", str(OUT / "fastqc"), str(READS)])


class PrepareReference(luigi.Task):
    def requires(self):
        return InputFiles()

    def output(self):
        return luigi.LocalTarget(str(WORK / "reference.fna"))

    def run(self):
        WORK.mkdir(parents=True, exist_ok=True)
        with gzip.open(REF_GZ, "rb") as src:
            with Path(self.output().path).open("wb") as dst:
                shutil.copyfileobj(src, dst)


class ReferenceIndex(luigi.Task):
    def requires(self):
        return PrepareReference()

    def output(self):
        return {
            "mmi": luigi.LocalTarget(str(WORK / "reference.mmi")),
            "fai": luigi.LocalTarget(str(WORK / "reference.fna.fai")),
        }

    def run(self):
        run([str(MINIMAP2), "-d", str(WORK / "reference.mmi"), str(WORK / "reference.fna")])
        run(["samtools", "faidx", str(WORK / "reference.fna")])


class MapReads(luigi.Task):
    def requires(self):
        return {
            "fastqc": FastQCReads(),
            "index": ReferenceIndex(),
        }

    def output(self):
        return luigi.LocalTarget(str(WORK / f"{SAMPLE}.sam"))

    def run(self):
        run([str(MINIMAP2), "-a", str(WORK / "reference.mmi"), str(READS)], Path(self.output().path))


class BamFromSam(luigi.Task):
    def requires(self):
        return MapReads()

    def output(self):
        return luigi.LocalTarget(str(WORK / f"{SAMPLE}.bam"))

    def run(self):
        run(["samtools", "view", "-@", THREADS, "-bS", str(WORK / f"{SAMPLE}.sam")], Path(self.output().path))


class Flagstat(luigi.Task):
    def requires(self):
        return BamFromSam()

    def output(self):
        return luigi.LocalTarget(str(OUT / "flagstat.txt"))

    def run(self):
        run(["samtools", "flagstat", str(WORK / f"{SAMPLE}.bam")], Path(self.output().path))


class EvaluateMapping(luigi.Task):
    def requires(self):
        return Flagstat()

    def output(self):
        return luigi.LocalTarget(str(OUT / "mapping_status.txt"))

    def run(self):
        text = Path(self.input().path).read_text(encoding="utf-8")
        match = re.search(r"\bmapped\s+\(([0-9]+(?:\.[0-9]+)?)%\s*:", text)
        if not match:
            raise RuntimeError("mapped percent not found")

        percent = float(match.group(1))
        status = "OK" if percent > THRESHOLD else "not OK"
        Path(self.output().path).write_text(
            f"flagstat={self.input().path}\n"
            f"mapped_percent={percent:.2f}\n"
            f"threshold={THRESHOLD:.2f}\n"
            f"status={status}\n",
            encoding="utf-8",
        )


class SortBam(luigi.Task):
    def requires(self):
        return {
            "bam": BamFromSam(),
            "status": EvaluateMapping(),
        }

    def output(self):
        return {
            "bam": luigi.LocalTarget(str(WORK / f"{SAMPLE}.sorted.bam")),
            "bai": luigi.LocalTarget(str(WORK / f"{SAMPLE}.sorted.bam.bai")),
        }

    def run(self):
        run(["samtools", "sort", "-@", THREADS, "-o", str(WORK / f"{SAMPLE}.sorted.bam"), str(WORK / f"{SAMPLE}.bam")])
        run(["samtools", "index", str(WORK / f"{SAMPLE}.sorted.bam")])


class CallVariants(luigi.Task):
    def requires(self):
        return {
            "ref": PrepareReference(),
            "bam": SortBam(),
        }

    def output(self):
        return luigi.LocalTarget(str(WORK / f"{SAMPLE}.vcf"))

    def run(self):
        run(["freebayes", "-f", str(WORK / "reference.fna"), str(WORK / f"{SAMPLE}.sorted.bam")], Path(self.output().path))


class MappingQualityPipeline(luigi.Task):
    def requires(self):
        return {
            "status": EvaluateMapping(),
            "variants": CallVariants(),
        }

    def output(self):
        return luigi.LocalTarget(str(OUT / "pipeline_finished.txt"))

    def run(self):
        status_text = Path(self.input()["status"].path).read_text(encoding="utf-8")
        Path(self.output().path).write_text(f"Finished\n{status_text}", encoding="utf-8")


if __name__ == "__main__":
    luigi.run()
