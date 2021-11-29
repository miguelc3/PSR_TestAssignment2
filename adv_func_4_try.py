#!/usr/bin/python3

import random
import numpy as np
import cv2

radius = 50
rangeX = (0, 500)
rangeY = (0, 500)
qty = 15  # or however many points you want

# Generate a set of all points within 200 of the origin, to be used as offsets later
# There's probably a more efficient way to do this.
deltas = set()
for x in range(-radius, radius+1):
    for y in range(-radius, radius+1):
        if x*x + y*y <= radius*radius:
            deltas.add((x, y))

randPoints = []
excluded = set()
i = 0
while i<qty:
    x = random.randrange(*rangeX)
    y = random.randrange(*rangeY)
    if (x, y) in excluded: continue
    randPoints.append((x, y))
    i += 1
    excluded.update((x+dx, y+dy) for (dx, dy) in deltas)

print(randPoints)
pts = np.array(randPoints)

blanck_image = 255*np.ones((500, 500), dtype=np.uint8)

cv2.polylines(blanck_image, pts=[pts], isClosed=True, color=(0, 0, 0), thickness=2)

cv2.imshow('lines', blanck_image)

cv2.waitKey(0)





