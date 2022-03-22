#
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 
#
# Copyright 2022 pipewe11
# 
# Permission is hereby granted, free of charge, to any person obtaining 
# a copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

import os
import sys
import re
import time
from collections import defaultdict
from datetime import datetime, timedelta

import ac
import acsys
 
import pickle

app_name = "TrackMap4"
version = "2022/03/20_00"

def acMain(ac_version):
    global appWindow
    global width, height
    global skip, skip2
    global track_name
    global T
    global carinfo
    global ncars
    global carnames

    width = 320
    height = 320
    skip = 0
    skip2 = 0

    appWindow = ac.newApp(app_name)
    ac.setTitle(appWindow, "Track Map")
    ac.setSize(appWindow, width, height)
    ac.drawBorder(appWindow, 0)
    ac.setBackgroundOpacity(appWindow, 0)

    track_name = ac.getTrackName(0)
    track_conf = ac.getTrackConfiguration(0)

    if len(track_conf) > 0:
        map_name = "{}%{}".format(track_name, track_conf)
        circuit = "{}/{}".format(track_name, track_conf)
    else:
        map_name = "{}".format(track_name)
        circuit = "{}".format(track_name)

    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maps")
    png_file = os.path.join(data_dir, map_name + ".png")
    pkl_file = os.path.join(data_dir, map_name + ".pkl")
    print(data_dir, png_file, pkl_file)

    if os.path.exists(png_file) and os.path.exists(pkl_file):
        ac.setBackgroundTexture(appWindow, png_file)

        with open(pkl_file, "rb") as f:
            T = pickle.load(f)

        ncars = ac.getCarsCount() 

        carnames = []
        for i in range(ncars):
            dn = ac.getDriverName(i)
            l = ac.addLabel(appWindow, dn)
            ac.setPosition(l, 0, 0)
            carnames += [l]

        ac.addRenderCallback(appWindow, onFormRender)

    return app_name

def acShutdown():

    return

def transform(U, v):

    r0 = U[0][0] * v[0] + U[0][1] * v[1] + U[0][2] * v[2]
    r1 = U[1][0] * v[0] + U[1][1] * v[1] + U[1][2] * v[2]
    r2 = 1 #U[2][0] * v[0] + U[2][1] * v[1] + U[2][2] * v[2]
    return (r0, r1, r2)

def update_names():
    global carnames

    for i, l in enumerate(carnames):
        if ac.isConnected(i) == 1:
            dn = ac.getDriverName(i)
            ac.setText(l, dn[:12])
        else:
            ac.setText(l, "")

def onFormRender(deltaT):
    global skip, skip2
    global carinfo
    global carnames
    global T
    
    if skip == 0:
        carinfo = []
        for i in range(ac.getCarsCount() - 1, -1, -1):
            if ac.isConnected(i) == 1:
                pos = ac.getCarState(i, acsys.CS.WorldPosition)
                if pos == 0:
                    p = (0, 0)
                else:
                    p = transform(T, [pos[0], -pos[2], 1])
                try:
                    lb = ac.getCarRealTimeLeaderboardPosition(i)
                except:
                    lb = 0
                carinfo += [(i, p, lb)]

                l = carnames[i]
                ac.setPosition(l, p[0], p[1])
            else:
                l = carnames[i]
                ac.setPosition(l, 0, 0)
        
    if skip2 == 0:
        update_names()

    opaque = 0.75
    for r in carinfo:
        i, p, lb = r
        if i == 0:
            ac.glColor4f(1.0, 1.0, 0.0, 1.0)
        else:
            if lb == 0:
                ac.glColor4f(1.0, 0.5, 1.0, opaque)
            else:
                ac.glColor4f(0.0, 0.75, 0.75, opaque)

        ac.glQuad(p[0] - 3, p[1] - 5, 6, 10)
        ac.glQuad(p[0] - 5, p[1] - 3, 10, 6)

    skip = (skip + 1) % 6
    skip2 = (skip2 + 1) % 240

