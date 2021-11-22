#!/usr/bin/python3

"""
# ----------------------------------------------------------
Test Assignment 2, PSR
ar_paint.py
MIGUEL PEREIRA
GABRIELE MICHELI
DIOGO VIEIRA
----------------------------------------------------------
"""

# -------------------------------------
# IMPORT LIBRARIES
# -------------------------------------
import copy
import cv2
# import cv2 as cv
import argparse
import json
import numpy as np
import time
from colorama import Back, Fore, Style
import math
from functools import partial

#------------------------------------------
# Global variables
#------------------------------------------
# To draw when use shake prevention
drawing_mouse = False
(yi_mouse, xi_mouse) = (None, None)
# To draw squares/rectangles
drawing_square = False
(xi_square, yi_square) = (None, None)


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


# ----------------------------------------------------------
# FUNCTION TO DRAW ON WINDOW CANVAS
# ----------------------------------------------------------
def canvas_paint(window, color, image, points, thickness, shake_prevention):

    if shake_prevention:
        # Check if distance < threshold -> draw line
        dist = math.dist(points[-1], points[-2])
        if dist < 20:
            # Draw line
            cv2.line(image, points[-1], points[-2], color, thickness)
            cv2.imshow(window, image)
    # If shake prevention not activated -> draw line anyway
    else:
        # Draw line
        cv2.line(image, points[-1], points[-2], color, thickness)
        cv2.imshow(window, image)


# ------------------------------------------------------------------
# FUNCTION TO DRAW WITH MOUSE WHEN USE_SHAKE_PREVENTION IS ACTIVATED
# ------------------------------------------------------------------
def draw_mouse(event, x, y, flags, param, color, thickness):

    global drawing_mouse, xi_mouse, yi_mouse

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing_mouse = True
        print('Started painting at: (x, y) = ' + str(x) + ', ' + str(y))
        xi_mouse = x
        yi_mouse = y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing_mouse:
            cv2.line(param, (xi_mouse, yi_mouse), (x, y), color, thickness)
            xi_mouse = x
            yi_mouse = y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing_mouse = False
        cv2.line(param, (xi_mouse, yi_mouse), (x, y), color, thickness)
        print('Ended painting at: (x, y) = ' + str(x) + ', ' + str(y))

# ------------------------------------------------------------------
# FUNCTION TO DRAW SQUARE WITH MOUSE
# ------------------------------------------------------------------


# 1 step: save the mouse initial coordinates in a tuple (x,y)

# 2 step: print circle with color choosed. Adapt the dimension in function of the mouse movement

# 3 step: check if the key is pressed or not (WHILE)

# 4 step: if the key is pressed -> calculate radius as: distance(center,last_mouse_posiion)


# ---------------------------------------------------------
# MAIN FUNCTION
# ----------------------------------------------------------
def main():
    # ----------------------------------------------------------
    # INITIALIZATION
    # ----------------------------------------------------------

    # Define argparse
    parser = argparse.ArgumentParser(description='Augmented Reality Paint')
    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to the json file.')
    parser.add_argument('-usp', '--use_shake_prevention', action='store_true', help='Use shake prevention '
                        'to avoid unwanted lines')
    args = vars(parser.parse_args())

    # Use shake prevention? True/False
    shake_prevention = args['use_shake_prevention']

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
    color_centroid = (0, 0, 255)  # Red in BGR
    thickness_centroid = -1

    # Properties of the line
    thickness_line = 2

    # Initialize a white board to paint -> canvas
    canvas = 255*np.ones(frame.shape, dtype=np.uint8)
    cv2.imshow(window_canvas, canvas)

    # Black as pre defined color to paint
    color_paint = (0, 0, 0)
    centroids = []

    # Explain how the program runs
    print(Back.RED + '   ' + Style.RESET_ALL + ' Hello, welcome to our Augmented Reality Paint program :) '
          + Back.RED + '   ' + Style.RESET_ALL + '\n\n')
    print('This program will use the limits of segmentation defined on the Color Segmenter file')
    print('Use the segmented object to draw on the canvas window \n')
    print(Fore.BLUE + 'Special keys: ' + Style.RESET_ALL)
    print(Back.GREEN + '                                  ' + Style.RESET_ALL)
    print('r -> Change color to red')
    print('g -> Change color to green')
    print('b -> Change color to blue')
    print('+ -> Increase drawing thickness')
    print('- -> Decrease drawing thickness')
    print('c -> Clear canvas')
    print('w -> save image')
    print('v -> Print picture to draw')
    print('s -> Draw rectangle')
    print('o -> Draw circle')
    if shake_prevention:
        print('You are using shake prevention mode, you can also draw with the mouse')
    print(Back.GREEN + '                                  ' + Style.RESET_ALL + '\n')

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
            frame_gui = cv2.circle(frame_gui, centroid, radius, color_centroid, thickness_centroid)
            centroids.append(centroid)
            if len(centroids) == 1:
                centroids.append(centroids[0])
            # Paint using the centroid as pen -> canvas_paint function
            canvas_paint(window_canvas, color_paint, canvas, centroids, thickness_line, shake_prevention)

        # If the shake prevention mode is activated allow to paint with mouse
        if shake_prevention:
            draw_mouse_partial = partial(draw_mouse, color=color_paint, thickness=thickness_line)
            cv2.setMouseCallback(window_canvas, draw_mouse_partial, param=canvas)
            cv2.imshow(window_canvas, canvas)

        cv2.imshow(window_original, frame_gui)

        # key controls
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
        elif key == ord('c'):
            canvas = 255 * np.ones(frame.shape, dtype=np.uint8)
            cv2.imshow(window_canvas, canvas)
            print('You pressed "c" to clear canvas')
        elif key == ord('w'):
            t = time.ctime(time.time())
            t = t.replace(' ', '_')
            filename = 'drawing_' + t + '.png'
            result = cv2.imwrite(filename, canvas)
            if result:
                print('File saved successfully')
            else:
                print('Error in saving file')
        elif key == ord('+'):
            thickness_line += 1
            print('You increased the brush thickness to ' + str(thickness_line))
        elif key == ord('-'):
            if thickness_line > 1:
                thickness_line -= 1
                print('You decreased the brush thickness to ' + str(thickness_line))
            else:
                print('The thickness cant be decreased further')
        elif key == ord('v'):
            canvas = frame
            print('Picture taken! You can now draw on top of it!')
        elif key == ord('s'):
            # TODO: draw rectangle
            print('Drawing rectangle')

        elif key == ord('o'):
            drawing_flag = False
            # TODO: draw circle
            print('Drawing circle')
            cx, cy = largest_object(mask_frame, window_largest)
            center_coordinates = (cx,cy)
            while drawing_flag == False:
                stop_key = cv2.waitKey(10)
                if stop_key == ord('o'):
                    drawing_flag = True
                cx, cy = largest_object(mask_frame, window_largest)
                actual_coordinates = (cx, cy)
                radius = int(math.dist(center_coordinates, actual_coordinates))
                circle_image = cv2.circle(canvas, center_coordinates, radius, color_paint, thickness_line)
                cv2.imshow(window_canvas, circle_image)


if __name__ == '__main__':
    main()