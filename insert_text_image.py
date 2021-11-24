#!/usr/bin/python3

import cv2
path = 'tree.jpg'

img = cv2.imread(path)

font = cv2.FONT_HERSHEY_SIMPLEX

i = 10
while(1):
    cv2.imshow('img',img)
    k = cv2.waitKey(33)
    if k==27:    # Esc key to stop
        break
    elif k==-1:  # normally -1 returned,so don't print it
        continue
    else:
        print(k) # else print its value

        cv2.putText(img, chr(k), (i, 50), font, 1, (0, 255, 0), 1, cv2.LINE_AA)
        i+=15

cv2.waitKey(0)
cv2.destroyAllWindows()