# image-sorter

![image-sorter](https://blog.hubspot.com/hubfs/how-to-sort-in-excel.jpg)

## Sort Duplicate Images in Bulk

### Requirements

- Python 3.x
- PIP 3.x

**pngcrush** is used in an attempt to correct any bad file information. Please ensure it is installed.

`sudo apt-get install pngcrush -y`

### Usage

Image Sorter will analyze and sort duplicates from the images/ directory.

Dependencies can be installed with pip:
`pip3 install -r requirements.txt`

The script can be ran with:
`python3 main.py`

### Options

- `-f`/`--faces` - Detect images w/ faces
- `-r`/`--rename` - Normalize Filenames (drop -1234 suffix)
- `-v`/`--verbose` - Increase output verbosity