from pathlib import Path
import argparse
import json
import os
import sys

from app.chequing import is_chequing, parse_chequing
from app.dedup import has_been_parsed, mark_as_parsed, upsert_schema
from app.entities import Config
from app.utils import format_transaction, write_file
from app.visa import is_visa, parse_visa


def parse_config(path: str) -> Config:
    try:
        with open(path, encoding="utf8") as json_file:
            return json.load(json_file)
    except Exception:
        return {}


def parse_files(path: str) -> list:
    files = []

    if os.path.isdir(path):
        files = [
            os.path.abspath(os.path.join(path, f))
            for f in os.listdir(path)
            if f.lower().endswith(".pdf")
                and not has_been_parsed(os.path.abspath(os.path.join(path, f)))
        ]
    elif os.path.isfile(path) and path.lower().endswith(".pdf"):
        files = [os.path.abspath(path)]

    return sorted(files)


def parse_args() -> tuple[list, dict, str]:
    parser = argparse.ArgumentParser(
        description="A script that parses RBC chequing and VISA statements in PDF format and extracts transactions"
    )

    parser.add_argument("path", help="Path or to PDF or directory of PDFs")
    parser.add_argument("--config", "-c", help="Path to config file", default=".rc")
    parser.add_argument("--out", "-o", help="Path to output file")

    args = parser.parse_args()
    config = parse_config(args.config)

    if config.get("enable_dedup"):
        upsert_schema()

    files = parse_files(args.path)

    if len(files) == 0:
        print("No valid PDF files found in the specified directory.")
        sys.exit(1)

    return (files, config, args.out)


def parse_pdf(file_path: str, categories: dict, excludes: list) -> list:
    if is_chequing(file_path):
        return parse_chequing(file_path, categories, excludes)

    if is_visa(file_path):
        return parse_visa(file_path, categories, excludes)

    return []

def process_file(file, config, out_dir):
    transactions = sorted(
        [
            tx
            for tx in parse_pdf(file, config.get("categories"), config.get("excludes"))
        ],
        key=lambda tx: tx["date"],
    )
    out_str = config.get("format") + "\n"
    out_str += "\n".join(
        format_transaction(
            tx,
            template=config.get("format"),
            default_category="Other",
            padding=False,
        )
        for tx in transactions
    )

    mark_as_parsed(file)

    if out_dir:
        file_name = os.path.basename(file)
        filename_with_csv = os.path.splitext(file_name)[0] + '.csv'
        out_file =Path(out_dir) / filename_with_csv
        write_file(out_str, out_file)

    print(f"Parsing statements... OK: {len(transactions)} transaction(s)")

def main():
    files, config, out_file = parse_args()
    for file in files:
        process_file(file, config, out_file)


if __name__ == "__main__":
    main()
