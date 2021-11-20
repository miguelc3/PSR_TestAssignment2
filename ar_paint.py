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
    _, frame = capture.read()

    # Create windows
    window_original = 'Original'
    window_segmented = 'Segmented'
    window_largest = 'Mask Largest Component'
    window_canvas = 'Canvas'
    cv2.namedWindow(window_original, cv2.WINDOW_NORMAL)
    cv2.namedWindow(window_segmented, cv2.WINDOW_NORMAL)
    cv2.namedWindow(window_largest, cv2.WINDOW_NORMAL)
    cv2.namedWindow(window_canvas, cv2.WINDOW_NORMAL)

    # Properties of the circle that defines the object centroid
    radius = 2
    color_circle = (255, 0, 0)  # Blue in BGR
    thickness = 2

    # Initialize a white board to paint -> canvas
    canvas = 255*np.ones(frame.shape, dtype=np.uint8)
    cv2.imshow(window_canvas, canvas)

    # Black as pre defined color to paint
    color_paint = (0, 0, 0)

    # Explain how to execute the program
    print('Press any key to start')

    # ----------------------------------------------------------
    # EXECUTION
    # ----------------------------------------------------------
    while 1:
        _, frame = capture.read()
        # Create a copy of the frame to manipulate
        frame_gui = copy.deepcopy(frame)

        # Segment image -> segmented function
        mask_frame = segmented(frame_gui, mins, maxs, window_segmented)

        # Find largest objet and the respective centroid -> largest_object function
        cx, cy = largest_object(mask_frame, window_largest)
        centroid = (cx, cy)
        if centroid != (0, 0):
            frame_gui = cv2.circle(frame_gui, centroid, radius, color_circle, thickness)
            canvas_paint(window_canvas, color_paint, centroid, canvas)

        cv2.imshow(window_original, frame_gui)

        key = cv2.waitKey(10)
        if key == ord('q'):
            print('You pressed "q" to exit. Good Bye!')
            break
        elif key == ord('g'):
            color_paint = (0, 255, 0)
            print('You press "g" to paint green')
        elif key == ord('r'):
            color_paint = (0, 0, 255)
            print('You press "r" to paint red')
        elif key == ord('b'):
            color_paint = (255, 0, 0)
            print('You press "b" to paint blue')


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
def largest_object(mask, window):
    # Initialize the the window of the largest object -> all black
    mask_largest = np.zeros(mask.shape, dtype=np.uint8)
    cv2.imshow(window, mask_largest)

    # Find the largest object
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    cnt = sorted(contours, key=cv2.contourArea)
    if len(cnt) > 0:
        largest = cnt[-1]
        cv2.fillPoly(mask_largest, pts=[largest], color=(255, 255, 255))

        # Find centroid
        m = cv2.moments(largest)
        if m['m00'] == 0:
            cx = 0
            cy = 0
        else:
            cx = int(m['m10'] / m['m00'])
            cy = int(m['m01'] / m['m00'])

    else:
        cx = 0
        cy = 0

    # Display the largest object
    cv2.imshow(window, mask_largest)
    return cx, cy


def canvas_paint(window, color, centroid, image):
    radius = 1
    thickness = 1
    cv2.circle(image, centroid, radius, color, thickness)
    cv2.imshow(window, image)


if __name__ == '__main__':
    main()
