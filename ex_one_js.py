import sys
import cv2
import os
from sys import platform
import argparse
import time
import numpy as np
import math
import pyttsx3
import winsound
import threading
import keyboard

import csv


# Body segment dimensions based on Winter data for 1.7M AND 65KG

m1 = 3.0225
m2 = 6.5
m3 = 16.1525
m4 = 1.82
m5 = 1.04
l1 = 0.47787
l2 = 0.42313
l3 = 0.4896
l4 = 0.3196
l5 = 0.2465
g = 9.81

# Uncomment and use for multiple trials

#"""
#Case 1


#Start at -90 and 0

low_shoulder = 170
high_shoulder = 180
mid_shoulder = 175
low_elbow = 65
high_elbow = 75
mid_elbow = 70
name = 'angle_data_js_t1'

#"""

"""
#Case 2

#Start at -90 and 0

low_shoulder = 160
high_shoulder = 165
low_elbow = 35
high_elbow = 45
name = 'angle_data_js_t2'

"""

"""
#Case 3

#Start at 0 and 0

low_shoulder = 125
high_shoulder = 135
low_elbow = 25
high_elbow = 35
name = 'angle_data_js_t3'

"""

"""
#Case 4

#Start at 0 and 0

low_shoulder = 140
high_shoulder = 150
low_elbow = 65
high_elbow = 75
name = 'angle_data_js_t4'

"""

"""
#Case 5

#Start at -90 and 0

low_shoulder = 155
high_shoulder = 165
low_elbow = 55
high_elbow = 65
name = 'angle_data_js_t5'

"""

sh = []
el =[]
timer =[]

try:
    # Import Openpose
    dir_path = os.path.dirname(os.path.realpath(__file__))
    try:

        if platform == "win32":

            sys.path.append(dir_path + '/../../python/openpose/Release');
            os.environ['PATH'] = os.environ['PATH'] + ';' + dir_path + '/../../x64/Release;' + dir_path + '/../../bin;'
            import pyopenpose as op
        else:
            sys.path.append('../../python');

            from openpose import pyopenpose as op
    except ImportError as e:

        raise e

    # Flags
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_dir", default="../../../examples/media/",
                        help="Process a directory of images. Read all standard formats (jpg, png, bmp, etc.).")
    parser.add_argument("--no_display", default=False, help="Enable to disable the visual display.")
    args = parser.parse_known_args()

    # Select Model folder and params
    params = dict()
    params["model_folder"] = "../../../models/"

    # Add others in path?
    for i in range(0, len(args[1])):
        curr_item = args[1][i]
        if i != len(args[1]) - 1:
            next_item = args[1][i + 1]
        else:
            next_item = "1"
        if "--" in curr_item and "--" in next_item:
            key = curr_item.replace('-', '')
            if key not in params:  params[key] = "1"
        elif "--" in curr_item and "--" not in next_item:
            key = curr_item.replace('-', '')
            if key not in params: params[key] = next_item

    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()

    # Read frames
    print("Reading video...")

    # Use when live feed not needed
    #input_source = 'body_data_new.MP4'

    cap = cv2.VideoCapture(0)
    Engine = pyttsx3.init()

    start = time.time()

    # Process and display images
    while True:

        hasFrame, frame = cap.read()


        datum = op.Datum()
        datum.cvInputData = frame
        opWrapper.emplaceAndPop([datum])

        # FUNCTION TO CALCULATE VECTOR LENGTH OF DETECTED JOINTS

        def vectors_length(x1, y1, x2, y2, x3, y3):

            p1 = math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
            p3 = math.sqrt((x2 - x3) * (x2 - x3) + (y2 - y3) * (y2 - y3))
            p2 = math.sqrt((x1 - x3) * (x1 - x3) + (y1 - y3) * (y1 - y3))

            if p1 * p2 == 0:
                angle = 0
                return angle
            else:
                z = (p1 * p1 + p2 * p2 - p3 * p3) / (2 * p1 * p2)

                if z > -1 and z < 1:
                    angle = math.pi - (math.acos(z))
                    return angle
                else:
                    angle = 0
                    return angle

        # FUNCTION TO SAVE DATA AS CSV FILE

        def save_data(elbow_angle, shoulder_angle):

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            with open(name + '.csv', 'a', newline='') as f:
                fieldname = ['Shoulder','Elbow','Time']
                writer = csv.writer(f)
                writer.writerow([math.degrees(shoulder_angle), math.degrees(elbow_angle),current_time])

        # FUNCTION FOR TEXT TO SPEECH AUDIO FEEDBACK

        def voice_command(elbow_angle, shoulder_angle):

            # stop recording when key is pressed
            if keyboard.is_pressed("p") is False:


                newVoiceRate = 200
                Engine.setProperty('rate', newVoiceRate)


                if (-high_shoulder <= math.degrees(shoulder_angle) <= -low_shoulder and low_elbow <= math.degrees(
                        elbow_angle) <= high_elbow):
                    winsound.Beep(2500,100)

                if (-low_shoulder <= math.degrees(shoulder_angle)):

                    amount_movement = math.fabs(round(math.fabs(math.degrees(shoulder_angle))) - low_shoulder)

                    if amount_movement <= 5:
                        Engine.say('Move arm slightly down')
                        Engine.runAndWait()
                        if Engine.isBusy():
                            save_data(elbow_angle, shoulder_angle)
                    else:
                        Engine.say('Move arm down bye' + str(amount_movement) + "degrees")
                        Engine.runAndWait()


                if math.degrees(shoulder_angle) <= -high_shoulder:
                    amount_movement = math.fabs(round(math.fabs(math.degrees(shoulder_angle))) - high_shoulder)

                    if amount_movement <= 5:
                        Engine.say('Move arm slightly up')
                        Engine.runAndWait()

                    else:

                        Engine.say('Move arm up bye' + str(amount_movement) + "degrees")
                        Engine.runAndWait()


                if math.degrees(elbow_angle) > high_elbow:
                    amount_movement = math.fabs(round(math.fabs(math.degrees(elbow_angle))) - high_elbow)
                    Engine.say('Extend elbow bye' + str(amount_movement) + "degrees")
                    Engine.runAndWait()


                if math.degrees(elbow_angle) < low_elbow:
                    amount_movement = math.fabs(round(math.fabs(math.degrees(elbow_angle))) - low_elbow)

                    Engine.say('Flex elbow bye' + str(amount_movement) + "degrees")
                    Engine.runAndWait()

                else :
                    t2.join()


        # Joints of interest ( Elbow, Shoulder, Wrist and Hip )

        R_elb_x = datum.poseKeypoints[0, 3][0]
        R_elb_y = datum.poseKeypoints[0, 3][1]

        R_sho_x = datum.poseKeypoints[0, 2][0]
        R_sho_y = datum.poseKeypoints[0, 2][1]

        R_wrist_x = datum.poseKeypoints[0, 4][0]
        R_wrist_y = datum.poseKeypoints[0, 4][1]

        R_hip_x = datum.poseKeypoints[0, 9][0]
        R_hip_y = datum.poseKeypoints[0, 9][1]

        # Joint angles based on vector length of concerned joints

        elbow_angle = (vectors_length(R_elb_x, R_elb_y, R_sho_x, R_sho_y, R_wrist_x, R_wrist_y))
        shoulder_angle = -(vectors_length(R_sho_x, R_sho_y, R_elb_x, R_elb_y, R_hip_x, R_hip_y))



        # Multi-thread data recording and voice output

        t1 = threading.Thread(target=save_data, args=[elbow_angle, shoulder_angle])
        t2 = threading.Thread(target=voice_command, args=[elbow_angle, shoulder_angle])
        t1.start()
        t2.start()



        if not args[0].no_display:
            cv2.imshow(datum.cvOutputData)
            key = cv2.waitKey(1)
            if key == 27: break



    end = time.time()
    print("Voice based feedback experiment completed in " + str(end - start) + " seconds")

except Exception as e:
    print(e)
    sys.exit(-1)
