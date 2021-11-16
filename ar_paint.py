#!/usr/bin/python3

# -------------------------------------
# IMPORT LIBRARIES
# -------------------------------------
import copy
import cv2
import argparse
import json
import numpy as np


# ----------------------------------------------------------
# MAIN FUNCTION
# ----------------------------------------------------------
def main():

    # ----------------------------------------------------------
    # INITIALIZATION
    # ----------------------------------------------------------

    # Define argparse
    parser = argparse.ArgumentParser(description='Augmented Reality Paint')
    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to the json file.')
    args = vars(parser.parse_args())

    # Load limits from json file
    with open(args['json']) as json_file:
        limits = json.load(json_file)

    mins = [limits['limits']['B']['min'], limits['limits']['G']['min'], limits['limits']['R']['min']]
    maxs = [limits['limits']['B']['max'], limits['limits']['G']['max'], limits['limits']['R']['max']]

    # Define a video capture object
    capture = cv2.VideoCapture(0)

    # Create windows
    window_original = 'Original'
    window_segmented = 'Segmented'
    window_largest = 'Mask Largest Component'
    window_canvas = 'Canvas'
    cv2.namedWindow(window_original, cv2.WINDOW_NORMAL)
    cv2.namedWindow(window_segmented, cv2.WINDOW_NORMAL)
    cv2.namedWindow(window_largest, cv2.WINDOW_NORMAL)
    cv2.namedWindow(window_canvas, cv2.WINDOW_NORMAL)

    # ----------------------------------------------------------
    # EXECUTION
    # ----------------------------------------------------------
    while 1:
        _, frame = capture.read()
        # Create a copy of the frame to manipulate
        frame_gui = copy.deepcopy(frame)

        cv2.imshow(window_original, frame_gui)

        mask_frame = segmented(frame_gui, mins, maxs, window_segmented)
        mask_largest = np.zeros(mask_frame.shape, dtype=np.uint8)
        cv2.imshow(window_largest, mask_largest)
        largest_object(mask_frame, mask_largest, window_largest)

        key = cv2.waitKey(10)
        if key == ord('q'):
            print('You pressed "q" to exit. Good Bye!')
            break


# ----------------------------------------------------------
# FUNCTION TO SEGMENT IMAGE WITH THE LIMITS FROM THE JSON FILE
# ----------------------------------------------------------
def segmented(frame, mins, maxs, window):
    mask_frame = cv2.inRange(frame, np.array(mins), np.array(maxs))
    cv2.imshow(window, mask_frame)

    return mask_frame


# ----------------------------------------------------------
# FUNCTION TO FIND THE LARGEST OBJECT AND THE CENTROID
# ----------------------------------------------------------
def largest_object(mask, img_draw, window):

    # Find the largest object
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    cnt = sorted(contours, key=cv2.contourArea)
    if len(cnt) > 0:
        largest = cnt[-1]
        cv2.fillPoly(img_draw, pts=[largest], color=(255, 255, 255))

    # Display the largest object
    cv2.imshow(window, img_draw)

    # Find centroid


if __name__ == '__main__':
    main()
