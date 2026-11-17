import csv
import re
from io import TextIOWrapper
from pathlib import Path
from zipfile import ZipFile


case_types = {"Requests for Street Cleaning"}
excluded_columns = {
    "case_enquiry_id",
    "sla_target_dt",
    "on_time",
    "case_status",
    "closure_reason",
    "case_title",
    "subject",
    "reason",
    "submitted_photo",
    "closed_photo",
}

data_folder = Path(__file__).resolve().parent.parent / "data"
archives = sorted(data_folder.glob("*.zip"))
if not archives:
    raise SystemExit(f"No ZIP archives found in {data_folder}")

with (data_folder / "street_cleaning.csv").open("w", encoding="utf-8", newline="") as output:
    writer = csv.writer(output)
    header = None
    for path in archives:
        with ZipFile(path) as archive:
            members = [
                name for name in archive.namelist()
                if name.lower().endswith(".csv") and not name.startswith("__MACOSX/")
            ]
            if len(members) != 1:
                raise ValueError(f"Expected one CSV in {path.name}")
            with TextIOWrapper(archive.open(members[0]), encoding="utf-8-sig", newline="") as source:
                rows = csv.reader(source)
                columns = next(rows)
                if header is None:
                    header = columns
                    type_column = header.index("type")
                    ward_column = header.index("ward")
                    output_columns = [i for i, name in enumerate(header) if name not in excluded_columns]
                    writer.writerow([header[i] for i in output_columns])
                elif columns != header:
                    raise ValueError(f"Unexpected CSV header in {path.name}")
                for row in rows:
                    if row[type_column] in case_types:
                        ward = re.fullmatch(r"(?:Ward\s+)?([0-9]+)", row[ward_column].strip(), re.IGNORECASE)
                        if ward:
                            row[ward_column] = f"{int(ward[1]):02d}"
                        writer.writerow([row[i] for i in output_columns])
