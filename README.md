# Google Takeout Photo Merger

Google Takeout splits your photos and metadata across multiple zip files. This script extracts and merges them into clean, year-organized folders — with no duplicates and no data loss.

## The Problem

When you export your Google Photos library via Google Takeout, your photos are spread across several zip files. A photo and its corresponding metadata file (e.g. `IMG_1234.jpg` and `IMG_1234.jpg.supplemental-metadata`) can end up in **different zip files**, even though they belong to the same `Photos from YYYY` folder. This makes it hard to work with your photos after exporting.

## What This Script Does

- Accepts zip files, already-unzipped folders, or a mix of both as input
- Automatically extracts any zip files before processing
- Scans all sources recursively to find every `Photos from YYYY` folder
- Merges all photos and metadata files for each year into a single output folder per year
- Skips exact duplicates silently
- Resolves filename conflicts safely by renaming instead of overwriting (e.g. `IMG_1234_2.jpg`)
- Saves a `merge_conflicts.log` file if any conflicts were detected
- Cleans up temporary extraction files automatically when done

## Requirements

- Python 3.6+
- No third-party packages — uses only the standard library

## Setup

**1. Clone or download this repo**

**2. Open `merge_google_takeout.py` and edit the CONFIG section at the top:**

```python
SOURCES = [
    r"C:\Users\YourName\Downloads\takeout-1.zip",
    r"C:\Users\YourName\Downloads\takeout-2.zip",
    r"C:\Users\YourName\Downloads\takeout-3.zip",
]

OUTPUT_DIR = r"C:\Users\YourName\Downloads\Google_Photos_Merged"
```

- `SOURCES` — list your zip files, unzipped folders, or any combination of both
- `OUTPUT_DIR` — where you want the merged result (will be created automatically)
- `KEEP_TEMP_EXTRACTION` — set to `True` if you want to keep the extracted zip contents after the script finishes (default: `False`)

**3. Run the script:**

```bash
python merge_google_takeout.py
```

## Example Output Structure

After running, your output folder will look like this:

```
Google_Photos_Merged/
├── Photos from 2015/
│   ├── IMG_0001.jpg
│   ├── IMG_0001.jpg.supplemental-metadata
│   └── ...
├── Photos from 2016/
│   └── ...
...
└── Photos from 2022/
    └── ...
```

## Notes

- The script **copies** files — your original zips and folders are never modified
- Works with any number of sources, not just 3
- Skipped years (years with no photos) are simply not created in the output
- If a `merge_conflicts.log` appears in your output folder, open it to review any renamed files
