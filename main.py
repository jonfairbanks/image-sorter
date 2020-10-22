#!/usr/bin/env python

from PIL import Image
import os
import hashlib
import sys
import shutil
import cv2
import numpy as np
from tqdm import tqdm

hashes = {}
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def fix_png(filename):
    if filename.endswith('.png'):
        try:
            img_location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), 'images', filename))
            cmd = 'pngcrush -q -ow -rem allb -reduce "' + img_location + '" > /dev/null 2>&1'
            os.system(cmd)
        except Exception as e:
            print(f'Error Fixing PNG: {filename}')
            pass

def detect_duplicates(filename):
    try:
        img_location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), 'images', filename))
        img_duplicate = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), 'duplicates', filename))

        if filename.endswith('.gif'):
            im = Image.open(img_location)
            im.seek(0)
            im.save("frame0.png")
            current_hash = hashlib.sha512(Image.open("frame0.png").tobytes()).hexdigest()
            try:
                os.remove("frame0.png")
            except OSError:
                pass
        else:
            current_hash = hashlib.sha512(Image.open(str(img_location)).tobytes()).hexdigest()

        if current_hash in hashes.keys():
            shutil.move(img_location, img_duplicate)
        else: 
            hashes[current_hash] = filename

    except Exception as e:
        print(f'Error Detecting Duplicate: {filename}')
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
                shutil.move(img_location, img_faces)

            try:
                os.remove("frame0.png")
            except OSError:
                pass
    except Exception as e:
        print(f'Error Detecting Faces: {filename} {e}')
        pass

def main():
    print('Searching images...\n')

    for filename in tqdm(sorted(os.listdir('images'))):
        if filename.endswith('.png'):
            fix_png(filename)
        detect_duplicates(filename)
        detect_faces(filename)

    print("\nImage processing completed!\n")

if __name__ == '__main__':
    if not os.path.exists('images'):
        raise Exception("No 'images/' directory found")

    if len(os.listdir('images')) == 0: 
        raise Exception("There are no images to process")

    if not os.path.exists('duplicates'):
        os.makedirs('duplicates')

    if not os.path.exists('faces'):
        os.makedirs('faces')

    main()