#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import luigi


ROOT_DIR = Path(__file__).resolve().parents[1]


class HelloWorld(luigi.Task):
    message = luigi.Parameter(default="Hello Luigi from Assignment 3")

    def output(self):
        return luigi.LocalTarget(str(ROOT_DIR / "results" / "hello_luigi.txt"))

    def run(self):
        Path(self.output().path).parent.mkdir(parents=True, exist_ok=True)
        with self.output().open("w") as out:
            out.write(f"{self.message}\n")


if __name__ == "__main__":
    luigi.run()
