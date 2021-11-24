#!/usr/bin/python3

# divide screen in zones

# Image path, number of rows and number of columns should be provided as an arguments
import cv2
import os

font = cv2.FONT_HERSHEY_SIMPLEX

if not os.path.exists('patches'):
    os.makedirs('patches')

nRows = 2 # Number of rows
mCols = 2 # Number of columns

img = cv2.imread('tree.jpg') # Reading image

cv2.imshow('tree.jpg',img) # Print img

# Dimensions of the image
sizeX = img.shape[1]
sizeY = img.shape[0]

print(img.shape)
i = 10

for i in range(0,nRows):
    for j in range(0, mCols):
        roi = img[int(i*sizeY/nRows):int(i*sizeY/nRows + sizeY/nRows),int(j*sizeX/mCols):int(j*sizeX/mCols+sizeX/mCols)]

        flag = False
        while not flag:
            shift = int(input("Please enter a number in the range [1,4]: "))
            if shift in range(1, 5):
                flag = True
                print(int(shift))
            else:
                print('Value outside range [1,4]. Try again')
        text = str(shift)

        roi = cv2.putText(roi, text, (50, 50), font, 1, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.imshow('rois'+str(i)+str(j), roi)
        cv2.imwrite('patches/patch_'+str(i)+str(j)+".jpg", roi)

cv2.waitKey(0)
cv2.destroyAllWindows()