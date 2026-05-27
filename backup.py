d
+# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 22:21:57 2026

@author: THIRUMALESHA M
"""

import numpy as np
import cv2
from collections import deque

def setvalues(x):
    pass  


cv2.namedWindow("color detectors")


cv2.createTrackbar("upper Hue", "color detectors", 153, 180, setvalues)
cv2.createTrackbar("upper Saturation", "color detectors", 255, 255, setvalues)
cv2.createTrackbar("upper Value", "color detectors", 255, 255, setvalues)


cv2.createTrackbar("lower Hue", "color detectors", 64, 180, setvalues)
cv2.createTrackbar("lower Saturation", "color detectors", 72, 255, setvalues)
cv2.createTrackbar("lower Value", "color detectors", 49, 255, setvalues)


bpoints = [deque(maxlen=1024)]
gpoints = [deque(maxlen=1024)]
rpoints = [deque(maxlen=1024)]
ypoints = [deque(maxlen=1024)]

blue_index = 0
green_index = 0
red_index = 0
yellow_index = 0

kernel = np.ones((5, 5), np.uint8)

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
colorIndex = 0


paintwindow = np.zeros((471, 636, 3)) + 255
paintwindow = cv2.rectangle(paintwindow, (40, 1), (140, 65), (0, 0, 0), 2)
paintwindow = cv2.rectangle(paintwindow, (160, 1), (255, 65), colors[0], -1)
paintwindow = cv2.rectangle(paintwindow, (275, 1), (370, 65), colors[1], -1)
paintwindow = cv2.rectangle(paintwindow, (390, 1), (485, 65), colors[2], -1)
paintwindow = cv2.rectangle(paintwindow, (505, 1), (600, 65), colors[3], -1)

cv2.putText(paintwindow, "CLEAR", (49, 33), cv2.FONT_HERSHEY_SIMPLEX,
            0.5, (0, 0, 0), 2, cv2.LINE_AA)


cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get trackbar positions
    u_hue = cv2.getTrackbarPos("upper Hue", "color detectors")
    u_saturation = cv2.getTrackbarPos("upper Saturation", "color detectors")
    u_value = cv2.getTrackbarPos("upper Value", "color detectors")

    l_hue = cv2.getTrackbarPos("lower Hue", "color detectors")
    l_saturation = cv2.getTrackbarPos("lower Saturation", "color detectors")
    l_value = cv2.getTrackbarPos("lower Value", "color detectors")

    upper_hsv = np.array([u_hue, u_saturation, u_value])
    lower_hsv = np.array([l_hue, l_saturation, l_value])

    
    frame = cv2.rectangle(frame, (40, 1), (140, 65), (0, 0, 0), -1)
    frame = cv2.rectangle(frame, (160, 1), (255, 65), colors[0], -1)
    frame = cv2.rectangle(frame, (275, 1), (370, 65), colors[1], -1)
    frame = cv2.rectangle(frame, (390, 1), (485, 65), colors[2], -1)
    frame = cv2.rectangle(frame, (505, 1), (600, 65), colors[3], -1)
    cv2.putText(frame, "CLEAR", (49, 33), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (255, 255, 255), 2, cv2.LINE_AA)

    
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.dilate(mask, kernel, iterations=1)

    
    cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None

    if len(cnts) > 0:
        cnt = sorted(cnts, key=cv2.contourArea, reverse=True)[0]
        ((x, y), radius) = cv2.minEnclosingCircle(cnt)
        cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
        M = cv2.moments(cnt)
        if M['m00'] != 0:
            center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        if center is not None:
            if center[1] <= 65:
                if 40 <= center[0] <= 140:
                    bpoints = [deque(maxlen=512)]
                    gpoints = [deque(maxlen=512)]
                    rpoints = [deque(maxlen=512)]
                    ypoints = [deque(maxlen=512)]
                    blue_index = green_index = red_index = yellow_index = 0
                    paintwindow[67:, :, :] = 255
                elif 160 <= center[0] <= 255:
                    colorIndex = 0  # blue
                elif 275 <= center[0] <= 370:
                    colorIndex = 1  # green
                elif 390 <= center[0] <= 485:
                    colorIndex = 2  # red
                elif 505 <= center[0] <= 600:
                    colorIndex = 3  # yellow
            else:
                if colorIndex == 0:
                    bpoints[blue_index].appendleft(center)
                elif colorIndex == 1:
                    gpoints[green_index].appendleft(center)
                elif colorIndex == 2:
                    rpoints[red_index].appendleft(center)
                elif colorIndex == 3:
                    ypoints[yellow_index].appendleft(center)
        else:
            bpoints.append(deque(maxlen=512))
            blue_index += 1
            gpoints.append(deque(maxlen=512))
            green_index += 1
            rpoints.append(deque(maxlen=512))
            red_index += 1
            ypoints.append(deque(maxlen=512))
            yellow_index += 1

    
    points = [bpoints, gpoints, rpoints, ypoints]
    for i in range(len(points)):
        for j in range(len(points[i])):
            for k in range(1, len(points[i][j])):
                if points[i][j][k - 1] is None or points[i][j][k] is None:
                    continue
                cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 2)
                cv2.line(paintwindow, points[i][j][k - 1], points[i][j][k], colors[i], 2)

    cv2.imshow("live drawing", frame)
    cv2.imshow("paint", paintwindow)
    cv2.imshow("mask", mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
