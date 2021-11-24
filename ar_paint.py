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
import argparse
import json
import numpy as np
import time
from colorama import Back, Fore, Style
import math
from functools import partial
import os

# ------------------------------------------
# Global variables
# ------------------------------------------
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
def largest_object(mask, window_draw, window_original, frame):
    # Initialize the the window of the largest object -> all black
    mask_largest = np.zeros(mask.shape, dtype=np.uint8)
    cv2.imshow(window_draw, mask_largest)

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
    cv2.imshow(window_draw, mask_largest)

    # make the object look "greener"
    cv2.add(frame, (-30, 80, -30, 0), dst=frame, mask=mask_largest)
    cv2.imshow(window_original, frame)

    return cx, cy


# ----------------------------------------------------------
# FUNCTION TO DRAW ON WINDOW CANVAS
# ----------------------------------------------------------
def canvas_paint(window, color, image, points, thickness, shake_prevention, circle_draw, rectangle_draw, stream, frame,
                 flip_vertical, flip_horizontal):

    if not circle_draw and not rectangle_draw:  # Checks if currently drawing a circle or a rectangle
        if shake_prevention:
            # Check if distance < threshold -> draw line
            # Also checks if it's painting a circle
            dist = math.dist(points[-1], points[-2])
            if dist < 20:
                cv2.line(image, points[-1], points[-2], color, thickness)
                if stream:
                    canvas_blend = img_blend(image, frame)
                    if not flip_vertical and not flip_horizontal:
                        cv2.imshow(window, canvas_blend)
                    if flip_vertical:
                        canvas_blend_inv = cv2.flip(canvas_blend, 0)
                        cv2.imshow(window, canvas_blend_inv)
                    if flip_horizontal:
                        canvas_blend_inv = cv2.flip(canvas_blend, 1)
                        cv2.imshow(window, canvas_blend_inv)

                else:
                    if not flip_vertical and not flip_horizontal:
                        cv2.imshow(window, image)
                    elif flip_vertical:
                        image_inv = cv2.flip(image, 0)
                        cv2.imshow(window, image_inv)
                    elif flip_horizontal:
                        image_inv = cv2.flip(image, 1)
                        cv2.imshow(window, image_inv)

        # If shake prevention not activated -> draw line anyway
        else:
            cv2.line(image, points[-1], points[-2], color, thickness)
            if stream:
                canvas_blend = img_blend(image, frame)
                if not flip_vertical and not flip_horizontal:
                    cv2.imshow(window, canvas_blend)
                elif flip_vertical:
                    canvas_blend_inv = cv2.flip(canvas_blend, 0)
                    cv2.imshow(window, canvas_blend_inv)
                elif flip_horizontal:
                    canvas_blend_inv = cv2.flip(canvas_blend, 1)
                    cv2.imshow(window, canvas_blend_inv)

            else:
                if not flip_vertical and not flip_horizontal:
                    cv2.imshow(window, image)
                elif flip_vertical:
                    image_inv = cv2.flip(image, 0)
                    cv2.imshow(window, image_inv)
                elif flip_horizontal:
                    image_inv = cv2.flip(image, 1)
                    cv2.imshow(window, image_inv)
    # ADD GABRIELE
    else:
        if shake_prevention:
                if stream:
                    canvas_blend = img_blend(image, frame)
                    if not flip_vertical and not flip_horizontal:
                        cv2.imshow(window, canvas_blend)
                    if flip_vertical:
                        canvas_blend_inv = cv2.flip(canvas_blend, 0)
                        cv2.imshow(window, canvas_blend_inv)
                    if flip_horizontal:
                        canvas_blend_inv = cv2.flip(canvas_blend, 1)
                        cv2.imshow(window, canvas_blend_inv)

                else:
                    if not flip_vertical and not flip_horizontal:
                        cv2.imshow(window, image)
                    elif flip_vertical:
                        image_inv = cv2.flip(image, 0)
                        cv2.imshow(window, image_inv)
                    elif flip_horizontal:
                        image_inv = cv2.flip(image, 1)
                        cv2.imshow(window, image_inv)
        else:
            if stream:
                canvas_blend = img_blend(image, frame)
                if not flip_vertical and not flip_horizontal:
                    cv2.imshow(window, canvas_blend)
                elif flip_vertical:
                    canvas_blend_inv = cv2.flip(canvas_blend, 0)
                    cv2.imshow(window, canvas_blend_inv)
                elif flip_horizontal:
                    canvas_blend_inv = cv2.flip(canvas_blend, 1)
                    cv2.imshow(window, canvas_blend_inv)
            else:
                if not flip_vertical and not flip_horizontal:
                    cv2.imshow(window, image)
                elif flip_vertical:
                    image_inv = cv2.flip(image, 0)
                    cv2.imshow(window, image_inv)
                elif flip_horizontal:
                    image_inv = cv2.flip(image, 1)
                    cv2.imshow(window, image_inv)
    # STOP ADD GABRIELE

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
# CREATE A BLEND IMAGE -> ADVANCED FUNCT 2
# ------------------------------------------------------------------
def img_blend(img, frame):

    # mask of white pix
    mins = np.array([255, 255, 255])
    maxs = np.array([255, 255, 255])
    mask_white = cv2.inRange(img, mins, maxs)

    # mask to bool
    mask_white = mask_white.astype(np.bool)

    # draw to stream
    frame_gui = copy.deepcopy(frame)
    frame_gui[~mask_white] = img[~mask_white]

    return frame_gui


# ------------------------------------------------------------------
# STUFF TO PRINT IN THE BEGINNING
# ------------------------------------------------------------------
def print_stuff(shake_prevention):
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
    print('t -> Drawing test')
    print('l -> Drawing test results')
    print('u -> Invert image vertically')
    print('h -> Invert image horizontally')
    if shake_prevention:
        print('You are using shake prevention mode, you can also draw with the mouse')
    print(Back.GREEN + '                                  ' + Style.RESET_ALL + '\n')


# ---------------------------------------------------------
# MAIN FUNCTION
# ----------------------------------------------------------
def main():
    # ----------------------------------------------------------
    # INITIALIZATION
    # ----------------------------------------------------------
    testing = False
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

    # Flag to check if we're drawing a circle
    circle_draw = False

    # Flag to check if we're drawing a rectangle
    rectangle_draw = False

    # Variable to show stream on canvas
    stream = False

    # Variable to chek if image inverted
    flip_vertical = False
    flip_horizontal = False

    # Explain how to use the program -> print_stuff function
    print_stuff(shake_prevention)

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
        cx, cy = largest_object(mask_frame, window_largest, window_original, frame_gui)  # make object green
        centroid = (cx, cy)
        if centroid != (0, 0):
            frame_gui = cv2.circle(frame_gui, centroid, radius, color_centroid, thickness_centroid)
            centroids.append(centroid)
            if len(centroids) == 1:
                centroids.append(centroids[0])
            # Paint using the centroid as pen -> canvas_paint function
            canvas_paint(window_canvas, color_paint, canvas, centroids, thickness_line, shake_prevention,
                         circle_draw, rectangle_draw, stream, frame, flip_vertical, flip_horizontal)

        # If the shake prevention mode is activated allow to paint with mouse
        if shake_prevention:
            draw_mouse_partial = partial(draw_mouse, color=color_paint, thickness=thickness_line)
            cv2.setMouseCallback(window_canvas, draw_mouse_partial, param=canvas)
            if not circle_draw and not rectangle_draw and not stream:
                cv2.imshow(window_canvas, canvas)
            elif stream and (circle_draw or rectangle_draw):
                # Replace image
                canvas_blend = img_blend(canvas, frame)
                cv2.imshow(window_canvas, canvas_blend)

        if not flip_vertical and not flip_horizontal:
            cv2.imshow(window_original, frame_gui)
        elif flip_vertical:
            frame_gui = cv2.flip(frame, 0)
            cv2.imshow(window_original, frame_gui)
        elif flip_horizontal:
            frame_gui = cv2.flip(frame, 1)
            cv2.imshow(window_original, frame_gui)

        # key controls
        key = cv2.waitKey(10)
        # q for quit
        if key == ord('q'):
            print('You pressed "q" to exit. Good Bye!')
            break

        # g to change color to green
        elif key == ord('g'):
            color_paint = (0, 255, 0)
            print('You press "g" to paint green')

        # r to change color to red
        elif key == ord('r'):
            color_paint = (0, 0, 255)
            print('You press "r" to paint red')

        # b to change color to blue
        elif key == ord('b'):
            color_paint = (255, 0, 0)
            print('You press "b" to paint blue')

        # c to clear canvas
        elif key == ord('c'):
            canvas = 255 * np.ones(frame.shape, dtype=np.uint8)
            cv2.imshow(window_canvas, canvas)
            print('You pressed "c" to clear canvas')

        # w to save image
        elif key == ord('w'):
            t = time.ctime(time.time())
            t = t.replace(' ', '_')
            filename = 'drawing_' + t + '.png'
            if not stream:
                result = cv2.imwrite(filename, canvas)
            else:
                result = cv2.imwrite(filename, img_blend(canvas, frame))

            if result:
                print('File saved successfully')
            else:
                print('Error in saving file')

        # + to increase the thickness
        elif key == ord('+'):
            thickness_line += 1
            print('You increased the brush thickness to ' + str(thickness_line))

        # - to decrease the thickness
        elif key == ord('-'):
            if thickness_line > 1:
                thickness_line -= 1
                print('You decreased the brush thickness to ' + str(thickness_line))
            else:
                print('The thickness cant be decreased further')

        # v to stream video on the window_canvas
        elif key == ord('v'):
            stream = ~stream
            if stream:
                print('You pressed "v". You can draw on top of the stream now')
            else:
                print('You pressed "v". You can draw on the canvas')

        # Extra -> flip the image vertically and horizontally
        # u for up -> vertically ... v was already taken for the second advanced functionality
        elif key == ord('u'):
            flip_vertical = not flip_vertical
            print('You pressed "u" to invert the image vertically')

        # h for horizontal
        elif key == ord('h'):
            flip_horizontal = not flip_horizontal
            print('You pressed "h" to invert the image horizontally')

        # o to draw circles
        elif key == ord('o'):
            if not circle_draw:
                circle_draw = True
                center_coordinates = centroid
                print("You are now drawing a circle")
            elif circle_draw:
                circle_draw = False
                canvas = cv2.circle(canvas, center_coordinates, circle_radius, color_paint, thickness_line)
                print("Circle finished!")

        # s to draw squares
        elif key == ord('s'):
            if not rectangle_draw:
                rectangle_draw = True
                start_coordinates = centroid
                print("You are now drawing a rectangle")
            elif rectangle_draw:
                rectangle_draw = False
                canvas = cv2.rectangle(canvas, start_coordinates, end_coordinates, color_paint, thickness_line)
                print("Rectangle finished!")


        elif key == ord('t'):

            testing = True #Boolean to check if test is occurring

            #Divide image into sections
            font = cv2.FONT_HERSHEY_SIMPLEX

            if not os.path.exists('patches'):
                os.makedirs('patches')

            nRows = 2  # Number of rows
            mCols = 2  # Number of columns

            img = cv2.imread('grid.jpeg')  # Reading image


            # Dimensions of the image
            sizeX = img.shape[1]
            sizeY = img.shape[0]

            i = 10

            color_list = []

            for i in range(0, nRows):
                for j in range(0, mCols):
                    roi = img[int(i * sizeY / nRows):int(i * sizeY / nRows + sizeY / nRows),
                          int(j * sizeX / mCols):int(j * sizeX / mCols + sizeX / mCols)]

                    flag = False
                    while not flag:
                        shift = int(input("Please enter a number in the range [1,4]: "))
                        if shift in range(1, 5):
                            flag = True
                            print(int(shift))
                        else:
                            print('Value outside range [1,4]. Try again')
                    text = str(shift)

                    color_list.append(shift)

                    roi = cv2.putText(roi, text, (50, 50), font, 1, (0, 255, 0), 1, cv2.LINE_AA)
                    # cv2.imshow('rois'+str(i)+str(j), roi)
                    cv2.imwrite('patch_' + str(i) + str(j) + ".jpg", roi)

            #Merging the images
            patch1 = cv2.imread('patch_00.jpg')
            patch2 = cv2.imread('patch_01.jpg')
            patch3 = cv2.imread('patch_10.jpg')
            patch4 = cv2.imread('patch_11.jpg')

            patch12 = cv2.hconcat([patch1, patch2])
            patch34 = cv2.hconcat([patch3, patch4])
            canvas = cv2.vconcat([patch12, patch34])

            h = canvas.shape[0]
            w = canvas.shape[1]

            print('Paint the sections in accordance with their numbering:')
            print('1 - Black;')
            print('2 - Blue;')
            print('3 - Red;')
            print('4 - Green;')

            print('When you\'re finished, press the \'l\' key to see how you did! :D')
            print(color_list)
            cv2.imshow(window_canvas, canvas)


        elif key == ord('l'):
            if testing:
                print('Let\'s see how you did!')
                testing = False

                for i in range(0, nRows):
                    for j in range(0, mCols):
                        roi = canvas[int(i * sizeY / nRows):int(i * sizeY / nRows + sizeY / nRows),
                              int(j * sizeX / mCols):int(j * sizeX / mCols + sizeX / mCols)]

                        cv2.imwrite('result_' + str(i) + str(j) + ".jpg", roi)

                part1 = cv2.imread('result_00.jpg')
                part2 = cv2.imread('result_01.jpg')
                part3 = cv2.imread('result_10.jpg')
                part4 = cv2.imread('result_11.jpg')


                #Evaluate part1
                mask1_black = cv2.inRange(part1, np.array([0, 0, 0]), np.array([10, 10, 10]))

                mask1_blue = cv2.inRange(part1, np.array([240, 0, 0]), np.array([255, 0, 0]))

                mask1_green = cv2.inRange(part1, np.array([0, 240, 0]), np.array([0, 255, 0]))

                mask1_red = cv2.inRange(part1, np.array([0, 0, 240]), np.array([0, 0, 255]))

                if color_list[0] == 1:
                    val1 = (mask1_black > 0).mean() * 100
                elif color_list[0] == 2:
                    val1 = (mask1_blue > 0).mean() * 100
                elif color_list[0] == 3:
                    val1 = (mask1_red > 0).mean() * 100
                elif color_list[0] == 4:
                    val1 = (mask1_green > 0).mean() * 100

                # Evaluate part2
                mask2_black = cv2.inRange(part2, np.array([0, 0, 0]), np.array([10, 10, 10]))

                mask2_blue = cv2.inRange(part2, np.array([240, 0, 0]), np.array([255, 0, 0]))

                mask2_green = cv2.inRange(part2, np.array([0, 240, 0]), np.array([0, 255, 0]))

                mask2_red = cv2.inRange(part2, np.array([0, 0, 240]), np.array([0, 0, 255]))

                if color_list[1] == 1:
                    val2 = (mask2_black > 0).mean() * 100
                elif color_list[1] == 2:
                    val2 = (mask2_blue > 0).mean() * 100
                elif color_list[1] == 3:
                    val2 = (mask2_red > 0).mean() * 100
                elif color_list[1] == 4:
                    val2 = (mask2_green > 0).mean() * 100


                # Evaluate part3
                mask3_black = cv2.inRange(part3, np.array([0, 0, 0]), np.array([10, 10, 10]))

                mask3_blue = cv2.inRange(part3, np.array([240, 0, 0]), np.array([255, 0, 0]))

                mask3_green = cv2.inRange(part3, np.array([0, 240, 0]), np.array([0, 255, 0]))

                mask3_red = cv2.inRange(part3, np.array([0, 0, 240]), np.array([0, 0, 255]))

                if color_list[2] == 1:
                    val3 = (mask3_black > 0).mean() * 100
                elif color_list[2] == 2:
                    val3 = (mask3_blue > 0).mean() * 100
                elif color_list[2] == 3:
                    val3 = (mask3_red > 0).mean() * 100
                elif color_list[2] == 4:
                    val3 = (mask3_green > 0).mean() * 100

                # Evaluate part4
                mask4_black = cv2.inRange(part4, np.array([0, 0, 0]), np.array([10, 10, 10]))

                mask4_blue = cv2.inRange(part4, np.array([240, 0, 0]), np.array([255, 0, 0]))

                mask4_green = cv2.inRange(part4, np.array([0, 240, 0]), np.array([0, 255, 0]))

                mask4_red = cv2.inRange(part4, np.array([0, 0, 240]), np.array([0, 0, 255]))

                if color_list[3] == 1:
                    val4 = (mask4_black > 0).mean() * 100
                elif color_list[3] == 2:
                    val4 = (mask4_blue > 0).mean() * 100
                elif color_list[3] == 3:
                    val4 = (mask4_red > 0).mean() * 100
                elif color_list[3] == 4:
                    val4 = (mask4_green > 0).mean() * 100


                score = (val1 + val2+ val3 + val4)/4

                print('You scored ' + str(score) +'%!')
            else:
                print('You have to start the test before get the results')
        elif circle_draw:
            actual_coordinates = centroid
            circle_radius = int(math.dist(center_coordinates, actual_coordinates))
            if not stream:
                image_circle = np.copy(canvas)
                image_circle = cv2.circle(image_circle, center_coordinates, circle_radius, color_paint, thickness_line)
                cv2.imshow(window_canvas, image_circle)
            else:
                canvas_blend = img_blend(canvas, frame)
                cv2.imshow(window_canvas, canvas_blend)
                image_circle = np.copy(canvas_blend)
                image_circle = cv2.circle(image_circle, center_coordinates, circle_radius, color_paint, thickness_line)
                cv2.imshow(window_canvas, image_circle)

        elif rectangle_draw:
            end_coordinates = centroid
            if not stream:
                image_rectangle = np.copy(canvas)
                image_rectangle = cv2.rectangle(image_rectangle, start_coordinates, end_coordinates, color_paint,
                                                thickness_line)
                cv2.imshow(window_canvas, image_rectangle)
            else:
                canvas_blend = img_blend(canvas, frame)
                cv2.imshow(window_canvas, canvas_blend)
                image_rectangle = np.copy(canvas_blend)
                image_rectangle = cv2.rectangle(image_rectangle, start_coordinates, end_coordinates, color_paint,
                                                thickness_line)
                cv2.imshow(window_canvas, image_rectangle)


        # Display stream on canvas
        '''
        # I think this part is not necessary, it is already on the draw_canvas function
        elif stream:
            # Replace image
            canvas_blend = img_blend(canvas, frame)
            if not flip_vertical:
                cv2.imshow(window_original, canvas_blend)
            else:
                canvas_blend_inv = cv2.flip(canvas_blend, 0)
                cv2.imshow(window_original, canvas_blend_inv)
        '''

    # ---------------------------------------------------
    # Terminating
    # ---------------------------------------------------
    capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
