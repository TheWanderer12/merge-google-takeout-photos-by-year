"""
merge_google_takeout.py
-----------------------
Merges Google Takeout exports — zip files or already-unzipped folders —
combining photos and metadata by year-named folders (e.g. "Photos from 2022")
into a single output directory.

Usage:
    1. Place this script anywhere on your computer.
    2. Edit the CONFIG section below.
    3. Run: python merge_google_takeout.py
"""

import zipfile
import shutil
import re
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIG — edit these paths before running
# ─────────────────────────────────────────────

# Paths to your Takeout exports.
# Each entry can be a .zip file OR an already-unzipped folder — mix and match freely.
SOURCES = [
    r"C:\Users\YourName\Downloads\takeout-1.zip",
    r"C:\Users\YourName\Downloads\takeout-2.zip",
    r"C:\Users\YourName\Downloads\takeout-3.zip",
]

# Where to put the merged output (will be created if it doesn't exist)
OUTPUT_DIR = r"C:\Users\YourName\Downloads\Google_Photos_Merged"

# If True, keeps the temporary folder used to extract zip files after the script finishes.
# If False (default), it is deleted automatically once merging is complete.
KEEP_TEMP_EXTRACTION = False

# ─────────────────────────────────────────────
# SCRIPT — no edits needed below this line
# ─────────────────────────────────────────────

YEAR_FOLDER_PATTERN = re.compile(r"Photos from \d{4}", re.IGNORECASE)
TEMP_DIR = Path(OUTPUT_DIR) / "_temp_extraction"


def prepare_sources():
    """
    Returns a list of folder paths to scan.
    Zip files are extracted to a temp folder first; plain folders are used as-is.
    """
    scan_dirs = []

    for i, source in enumerate(SOURCES, 1):
        source = Path(source)

        if not source.exists():
            print(f"  ⚠️  WARNING: Source not found, skipping: {source}")
            continue

        if source.suffix.lower() == ".zip":
            dest = TEMP_DIR / f"zip_{i}"
            dest.mkdir(parents=True, exist_ok=True)
            print(f"  → Extracting {source.name} ...")
            with zipfile.ZipFile(source, "r") as zf:
                zf.extractall(dest)
            scan_dirs.append(dest)
        elif source.is_dir():
            print(f"  → Using folder: {source.name}")
            scan_dirs.append(source)
        else:
            print(f"  ⚠️  WARNING: Unrecognized source (not a .zip or folder), skipping: {source}")

    return scan_dirs


def find_year_folders(scan_dirs):
    """Walk all source dirs and collect all year-named folders."""
    year_folders = {}  # { "Photos from 2022": [path1, path2, ...], ... }

    for source in scan_dirs:
        for folder in source.rglob("*"):
            if folder.is_dir() and YEAR_FOLDER_PATTERN.match(folder.name):
                year_folders.setdefault(folder.name, []).append(folder)

    return year_folders


def merge_year_folders(year_folders):
    """Copy all files from each year folder into the merged output."""
    output_root = Path(OUTPUT_DIR)
    output_root.mkdir(parents=True, exist_ok=True)

    total_copied = 0
    total_skipped = 0
    conflict_log = []

    print(f"\n🗂️  Merging {len(year_folders)} year folder(s) into: {output_root}\n")

    for year_name in sorted(year_folders.keys()):
        source_dirs = year_folders[year_name]
        dest_dir = output_root / year_name
        dest_dir.mkdir(parents=True, exist_ok=True)

        file_count = 0
        skip_count = 0

        for src_dir in source_dirs:
            for src_file in src_dir.iterdir():
                if not src_file.is_file():
                    continue

                dest_file = dest_dir / src_file.name

                if dest_file.exists():
                    if files_are_identical(src_file, dest_file):
                        skip_count += 1  # Exact duplicate, safe to skip
                    else:
                        # Different file with same name — rename to avoid overwrite
                        new_name = resolve_conflict(dest_dir, src_file.name)
                        shutil.copy2(src_file, dest_dir / new_name)
                        conflict_log.append(
                            f"  CONFLICT: {year_name}/{src_file.name} → saved as {new_name}"
                        )
                        file_count += 1
                else:
                    shutil.copy2(src_file, dest_file)
                    file_count += 1

        print(f"  ✅ {year_name}: {file_count} file(s) copied, {skip_count} duplicate(s) skipped.")
        total_copied += file_count
        total_skipped += skip_count

    print(f"\n🎉 Done! {total_copied} files merged, {total_skipped} exact duplicates skipped.")

    if conflict_log:
        print(f"\n⚠️  {len(conflict_log)} filename conflict(s) were renamed:")
        for line in conflict_log:
            print(line)

        log_path = output_root / "merge_conflicts.log"
        log_path.write_text("\n".join(conflict_log), encoding="utf-8")
        print(f"\n   Full conflict log saved to: {log_path}")


def files_are_identical(file_a: Path, file_b: Path) -> bool:
    """Quick check: same size first, then byte-by-byte if needed."""
    if file_a.stat().st_size != file_b.stat().st_size:
        return False
    return file_a.read_bytes() == file_b.read_bytes()


def resolve_conflict(dest_dir: Path, filename: str) -> str:
    """Generate a non-colliding filename by appending _2, _3, etc."""
    stem = Path(filename).stem
    suffix = "".join(Path(filename).suffixes)
    counter = 2
    while (dest_dir / f"{stem}_{counter}{suffix}").exists():
        counter += 1
    return f"{stem}_{counter}{suffix}"


def cleanup_temp():
    """Remove the temporary extraction directory."""
    if TEMP_DIR.exists():
        print(f"\n🧹 Cleaning up temp extraction folder...")
        shutil.rmtree(TEMP_DIR)
        print("  ✅ Temp files removed.")


def main():
    print("=" * 55)
    print("  Google Takeout Merger")
    print("=" * 55)

    print("\n📦 Preparing sources...")
    scan_dirs = prepare_sources()

    if not scan_dirs:
        print("\n❌ No valid sources found. Check your SOURCES paths in the CONFIG section.")
        return

    year_folders = find_year_folders(scan_dirs)

    if not year_folders:
        print("\n❌ No 'Photos from YYYY' folders found in the provided sources.")
        print("   Double-check your SOURCES paths in the CONFIG section.")
        return

    merge_year_folders(year_folders)

    if not KEEP_TEMP_EXTRACTION:
        cleanup_temp()

    print(f"\n📁 Your merged photos are in:\n   {OUTPUT_DIR}\n")


if __name__ == "__main__":
    main()
