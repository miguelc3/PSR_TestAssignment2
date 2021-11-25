#!/usr/bin/python3

"""
# ----------------------------------------------------------
Test Assignment 2, PSR
color_segmenter.py
MIGUEL PEREIRA
GABRIELE MICHELI
DIOGO VIEIRA
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
from colorama import Fore, Style, Back


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

    # Explain how the program works
    print(Back.RED + '   ' + Style.RESET_ALL + ' Welcome to our color_segmenter program :) '
          + Back.RED + '   ' + Style.RESET_ALL + '\n\n')
    print(Fore.BLUE + 'Use the trackbars to segment the three color channels of the image.' + Style.RESET_ALL)
    print('\nPress ' + Fore.BLUE + '"w"' + Style.RESET_ALL + ' when you\'re satisfied with the '
          'segmentation so that the values are saved in the file "limits.json".')
    print('\nPress ' + Fore.BLUE + '"q"' + Style.RESET_ALL + ' if you want to exit.\n')
    print(Fore.RED + 'ps: If you don\'t define any values for the segmentation limits, the predefined values'
          ' will be: min = 0 and max = 255 for all color channels (B, G and R)' + Style.RESET_ALL +
          '\n')

    # initial setup - define a video capture object
    capture = cv.VideoCapture(0)
    if capture.isOpened():
        print('\n' + Back.GREEN + 'Capturing video from webcam' + Style.RESET_ALL)
    else:
        print(Back.RED + 'Warning: Camera is not working' + Style.RESET_ALL)

    # window names
    window_original = 'Original'
    cv.namedWindow(window_original, cv.WINDOW_NORMAL)
    window_segmented = 'Segmented'
    cv.namedWindow(window_segmented, cv.WINDOW_NORMAL)

    # Predefined limits of segmentation - Accept all values of B G R
    limits_original = {'limits': {'B': {'max': 255, 'min': 0},
                                  'G': {'max': 255, 'min': 0},
                                  'R': {'max': 255, 'min': 0}}}

    # To print if the user does not press 'w'
    limits = copy.deepcopy(limits_original)

    # File to save the limits
    file_name = 'limits.json'
    with open(file_name, 'w') as file_handle:
        json.dump(str(limits), file_handle)

    # Partial function to avoid use global variables
    trackbar_partial = partial(trackbar, window=window_segmented, limits=limits)

    # Add trackbars to the segmented window
    cv.createTrackbar('min B', window_segmented, 0, 255, trackbar_partial)
    cv.createTrackbar('max B', window_segmented, 255, 255, trackbar_partial)
    cv.createTrackbar('min G', window_segmented, 0, 255, trackbar_partial)
    cv.createTrackbar('max G', window_segmented, 255, 255, trackbar_partial)
    cv.createTrackbar('min R', window_segmented, 0, 255, trackbar_partial)
    cv.createTrackbar('max R', window_segmented, 255, 255, trackbar_partial)

    # Variable to chek if the user saved any values for limits
    pressed_w = False

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

        # Keys to exit and save limits
        key = cv.waitKey(10)

        if key == ord('q'):
            # If the user press q -> quit
            print('\nYou typed ' + Fore.BLUE + '"q"' + Style.RESET_ALL + ' to exit, good bye!!')
            if not pressed_w:
                print(Fore.RED + Style.BRIGHT + '\nWARNING:' + Style.RESET_ALL)
                print('You didn\'t save any values of segmentation ...')
                print('\nThe predefined values for limits were saved:')
                print(limits_original)
            elif pressed_w:
                print('\nThe vales of the segmentation limits saved:')
                print(limits)
            break

        elif key == ord('w'):
            pressed_w = True
            # if the user press w -> write in the json file
            with open(file_name, 'w') as file_handle:
                print(Fore.GREEN + '** writing dictionary "limits" to file ' + file_name + ' **' + Style.RESET_ALL)
                json.dump(limits, file_handle)

if __name__ == '__main__':
    main()