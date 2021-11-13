#!/usr/bin/python3

"""
# ----------------------------------------------------------
Test Assignment 2, PSR
Miguel Pereira
...
...
----------------------------------------------------------
"""

# -------------------------------------
# IMPORT LIBRARIES
# -------------------------------------
import copy
import cv2 as cv
from functools import partial
import numpy as np
import json


# ----------------------------------------------------------
# FUNCTION TO UPDATE SEGMENTATION LIMITS
# ----------------------------------------------------------
def trackbar(_, window, limits):

    mins = [0, 0, 0]
    maxs = [0, 0, 0]

    mins[0] = cv.getTrackbarPos('min B', window)
    maxs[0] = cv.getTrackbarPos('max B', window)
    mins[1] = cv.getTrackbarPos('min G', window)
    maxs[1] = cv.getTrackbarPos('max G', window)
    mins[2] = cv.getTrackbarPos('min R', window)
    maxs[2] = cv.getTrackbarPos('max R', window)

    [limits['limits']['B']['min'], limits['limits']['G']['min'], limits['limits']['R']['min']] = mins
    [limits['limits']['B']['max'], limits['limits']['G']['max'], limits['limits']['R']['max']] = maxs

    return limits, mins, maxs


# ----------------------------------------------------------
# MAIN FUNCTION
# ----------------------------------------------------------
def main():
    # ----------------------------------------------------------
    # INITIALIZATION
    # ----------------------------------------------------------

    # initial setup - define a video capture object
    capture = cv.VideoCapture(0)

    # window names
    window_original = 'Original'
    cv.namedWindow(window_original, cv.WINDOW_NORMAL)
    window_segmented = 'Segmented'
    cv.namedWindow(window_segmented, cv.WINDOW_NORMAL)

    # Predefined limits of segmentation - Accept all values of B G R
    limits = {'limits': {'B': {'max': 255, 'min': 0},
                         'G': {'max': 255, 'min': 0},
                         'R': {'max': 255, 'min': 0}}}

    # Partial function to avoid use global variables
    trackbar_partial = partial(trackbar, window=window_segmented, limits=limits)

    # Add trackbars to the segmented window
    cv.createTrackbar('min B', window_segmented, 0, 255, trackbar_partial)
    cv.createTrackbar('max B', window_segmented, 255, 255, trackbar_partial)
    cv.createTrackbar('min G', window_segmented, 0, 255, trackbar_partial)
    cv.createTrackbar('max G', window_segmented, 255, 255, trackbar_partial)
    cv.createTrackbar('min R', window_segmented, 0, 255, trackbar_partial)
    cv.createTrackbar('max R', window_segmented, 255, 255, trackbar_partial)

    # ----------------------------------------------------------
    # EXECUTION
    # ----------------------------------------------------------
    while True:
        # Capture video frame
        _, frame = capture.read()
        frame_gui = copy.deepcopy(frame)

        # Display frame
        cv.imshow(window_original, frame_gui)

        # Get the updated value from tracbars
        limits, mins, maxs = trackbar_partial(0)

        # Segment the image and display the result
        mask_frame = cv.inRange(frame_gui, np.array(mins), np.array(maxs))
        cv.imshow(window_segmented, mask_frame)

        # print(limits)

        # Keys to exit and save limits
        key = cv.waitKey(10)
        if key == ord('q'):
            # If the user press q -> quit
            print('You typed "q" to exit')
            break
        elif key == ord('w'):
            # if the user press w -> write in the json file
            file_name = 'limits.json'
            with open(file_name, 'w') as file_handle:
                print('writing dictionary "limits" to file ' + file_name)
                json.dump(str(limits), file_handle)


if __name__ == '__main__':
    main()
