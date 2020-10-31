#!/usr/bin/env python

from PIL import Image
import os
import hashlib
import sys
import shutil
import cv2
import numpy as np
from tqdm import tqdm
import re
import argparse

parser = argparse.ArgumentParser(description='Sort Duplicate Images in Bulk')
parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
parser.add_argument("-r", "--rename", help="Normalize filenames (drop -1234 suffix)", action="store_true")
parser.add_argument("-f", "--faces", help="Detect images w/ faces", action="store_true")
args = parser.parse_args()
if args.verbose:
    print("** Verbosity: ON **\n")

hashes = {}
pattern = '([0-9a-zA-Z]*)(\-[0-9]+)'
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def fix_png_data(filename):
    if filename.endswith('.png'):
        try:
            img_location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), 'images', filename))
            if args.verbose:
                print(f'Fixing PNG: {filename}')
            cmd = 'pngcrush -q -ow -rem allb -reduce "' + img_location + '" > /dev/null 2>&1'
            os.system(cmd)
        except Exception as e:
            print(f'Error Fixing PNG: {filename} {e}')
            pass

def detect_duplicates(filename):
    try:
        img_location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), 'images', filename))
        img_duplicate = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), 'duplicates', filename))

        if filename.endswith('.gif'):
            im = Image.open(img_location)
            im.seek(1)
            im.save("frame1.png")
            current_hash = hashlib.sha512(Image.open("frame1.png").tobytes()).hexdigest()
            try:
                os.remove("frame1.png")
            except OSError:
                pass
        else:
            current_hash = hashlib.sha512(Image.open(str(img_location)).tobytes()).hexdigest()

        if current_hash in hashes.keys():
            if args.verbose:
                print(f'Duplicate Found: {filename}')
            shutil.move(img_location, img_duplicate)
        else: 
            hashes[current_hash] = filename

    except Exception as e:
        print(f'Error Detecting Duplicate: {filename} {e}')
        pass

def detect_faces(filename):
    try:
        img_location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), 'images', filename))
        img_faces = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), 'faces', filename))
        if os.path.exists(img_location):
            if filename.endswith('.gif'):
                im = Image.open(img_location)
                im.seek(0)
                im.save("frame0.png")
                try:
                    img = cv2.imread("frame0.png")
                except Exception as e:
                    raise Exception(f'File Error: {e}')
                    return
            else:
                try:
                    img = cv2.imread(img_location)
                except Exception as e:
                    raise Exception(f'File Error: {e}')
                    return

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.5,
                minNeighbors=1,
                minSize=(30, 30)
            )

            if len(faces) > 0:
                if args.verbose:
                    print(f'Detected Face(s): {filename}')
                shutil.move(img_location, img_faces)

            try:
                os.remove("frame0.png")
            except OSError:
                pass
    except Exception as e:
        print(f'Error Detecting Faces: {filename} {e}')
        pass

def normalize_filenames(filename):
    img_location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), 'images', filename))
    if os.path.exists(img_location):
        result = re.match(pattern, filename)
        if result and result[1]:
            ext = os.path.splitext(filename)[-1].lower()
            newimg_location = get_nonexistant_path(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), 'images', result[1])) + ext)
            if args.verbose:
                print(f"Renaming: {img_location} --> {newimg_location}")
            os.rename(img_location, newimg_location)
    return

def get_nonexistant_path(fname_path):
    if not os.path.exists(fname_path):
        return fname_path
    filename, file_extension = os.path.splitext(fname_path)
    i = 1
    new_fname = "{}-{}{}".format(filename, i, file_extension)
    while os.path.exists(new_fname):
        i += 1
        new_fname = "{}-{}{}".format(filename, i, file_extension)
    return new_fname

def main():
    print('Searching images...\n')

    for filename in tqdm(sorted(os.listdir('images'))):
        if filename.endswith('.png'):
            fix_png_data(filename)
        detect_duplicates(filename)
        if args.faces:
            detect_faces(filename)
        if args.rename:
            normalize_filenames(filename)
    
    hashes = {}
    print("\nImage processing completed!\n")
    return

if __name__ == '__main__':
    if not os.path.exists('images'):
        raise Exception("No 'images/' directory found")

    if len(os.listdir('images')) == 0: 
        raise Exception("There are no images to process")

    if not os.path.exists('duplicates'):
        os.makedirs('duplicates')

    if not os.path.exists('faces'):
        os.makedirs('faces')

    try:
        main()
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)