from tkinter import *
from PIL import Image
import cv2
import math
import numpy as np


class Tissue():
    def __init__(self, points, factor, dbit, num_chan):
        thresh = cv2.imread(dbit, cv2.IMREAD_UNCHANGED)


        for i in range(len(points)):
            points[i] /= factor

        #getting the slope of left * right lines
        ratioNum = (num_chan*2)-1
        leftS = self.ratio50l(points[0],points[1],points[6],points[7],ratioNum)
        topS = self.ratio50l(points[0],points[1],points[2],points[3],ratioNum)
        slope = [round(leftS[1]-points[1], 5), round(leftS[0]-points[0], 5)]
        slopeT = [round(topS[1]-points[1], 5), round(topS[0]-points[0], 5)]
        slopeO = [slope[0]*2, slope[1]*2]
        slopeTO = [slopeT[0]*2, slopeT[1]*2]


        dist= round(self.distance(points[0], points[1], points[2], points[3]), 5)
        distance = int(dist/99)

        p = round(self.distance(leftS[0], leftS[1], topS[0], topS[1]), 5)
        q = round(self.distance(points[0], points[1], topS[0]+slope[1], topS[1]+slope[0]), 5)
        self.spot_dia = math.sqrt(p*q)
        self.fud_dia = self.spot_dia*1.6153846

        numChannels = num_chan
        self.tixel_status = [[0 for i in range(numChannels)] for i in range(numChannels)]
        top = [0,0]
        left = [0,0]
        flag = False
        prev = [points[0],points[1]]
        corners = []
        for i in range(0, numChannels):
            top[0] = prev[0]+slopeT[1]
            top[1] = prev[1]+slopeT[0]
            flag = False
            for j in range(0, numChannels):
                corners = []
                if flag == False:
                    left[0] = prev[0]
                    left[1] = prev[1]
                    tL = [left[0],left[1]]
                    tR = [top[0],top[1]]
                    bL = [tL[0]+slope[1],tL[1]+slope[0]]
                    bR = [tR[0]+slope[1],tR[1]+slope[0]]
                    flag =  True
                else:
                    left[0] += slopeO[1]
                    left[1] += slopeO[0]
                    tL = [left[0],left[1]]
                    tR = [top[0],top[1]]
                    bL = [tL[0]+slope[1],tL[1]+slope[0]]
                    bR = [tR[0]+slope[1],tR[1]+slope[0]]

                corners.append(tL);corners.append(tR);corners.append(bR);corners.append(bL);
                if self.calculate_avg(thresh, corners, distance) > 242:
                    self.tixel_status[j][i] = 0
                else:
                    self.tixel_status[j][i] = 1

                top[0] += slopeO[1]
                top[1] += slopeO[0]
            prev[0] += slopeTO[1]
            prev[1] += slopeTO[0]

        self.theAnswer()

    def calculate_avg(self, pic, points, dist):
        """
        Vectorized average over quadrilateral area defined by 'points' on image 'pic'.
        points: list of four [x,y] (floats)
        pic: numpy array (grayscale) (height, width)
        dist: kept for compatibility but not used in this fast path
        Returns mean pixel value (float).
        """
        # Convert to floats and compute integer bounding box (clamped)
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        x_min = max(0, int(math.floor(min(xs))))
        x_max = min(pic.shape[1] - 1, int(math.ceil(max(xs))))
        y_min = max(0, int(math.floor(min(ys))))
        y_max = min(pic.shape[0] - 1, int(math.ceil(max(ys))))

        # Empty or degenerate region -> treat as background (white)
        if x_max < x_min or y_max < y_min:
            return 255.0

        # Create local polygon (shift coords to local box origin)
        poly = np.array([[[int(round(p[0])) - x_min, int(round(p[1])) - y_min] for p in points]], dtype=np.int32)

        # Create mask for bounding box and fill polygon
        h_box = y_max - y_min + 1
        w_box = x_max - x_min + 1
        mask = np.zeros((h_box, w_box), dtype=np.uint8)
        cv2.fillPoly(mask, poly, 1)

        # Slice the region from the image and compute mean only on masked pixels
        region = pic[y_min:y_max + 1, x_min:x_max + 1]
        vals = region[mask == 1]
        if vals.size == 0:
            return 255.0
        return float(vals.mean())

    def ratio50l(self,xc,yc,xr,yr,num):
        txp = xc + (1/(num))*(xr-xc)
        typ = yc + (1/(num))*(yr-yc)
        return [txp , typ]

    def coords(self, tL,tR,dis):
        coords = []
        coords.append(tL)
        for i in range(1,dis+1):
            txp = tL[0] + (i/(dis))*(tR[0]-tL[0])
            typ = tL[1] + (i/(dis))*(tR[1]-tL[1])
            coords.append([txp,typ])
        return coords
    def downCoords(self, points, dis):
        coords = []
        coords.append(points)
        for i in range(1, dis+1):
            y = points[1]+ i
            x = points[0]
            coords.append([x,y])
        return coords

    def distance(self,x1,y1,x2,y2):
        dis = (x1-x2)**2 + (y1-y2)**2
        return math.sqrt(dis)

    def theAnswer(self):
        return self.tixel_status,self.spot_dia,self.fud_dia
    