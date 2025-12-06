#!/usr/bin/env python3

# concat a list of input PNGs into an output video

import sys

import cv2

if len(sys.argv) < 3:
    print("usage: concat_pngs.py <output.mp4> <image1.png> <image2.png> ...")
    sys.exit(1)

output = sys.argv[1]
images = sys.argv[2:]

first_img = cv2.imread(images[0])
height, width = first_img.shape[:2]

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output, fourcc, 30.0, (width, height))

for img_path in images:
    img = cv2.imread(img_path)
    out.write(img)

out.release()
