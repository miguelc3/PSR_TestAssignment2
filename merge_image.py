#!/usr/bin/python3

import cv2
import numpy as np

img1 = cv2.imread('tree.jpg')
img2 = cv2.imread('tree.jpg')

vis = np.concatenate((img1, img2), axis=0)

cv2.imwrite('out1.jpg', vis)

