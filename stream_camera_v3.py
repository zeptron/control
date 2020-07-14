#python stream_camera.py --video=car.mp4 --ip=localhost --port=5555
#python stream_camera_v3.py --video=TownCentreXVID.mp4 --ip=localhost --port=5555
import sys
import socket
import time
import cv2
# import argparse
import os
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import imagezmq
import threading

# parser = argparse.ArgumentParser(description='Stream video parameters')
# parser.add_argument("--video", default="", help='Path to video file.')
# parser.add_argument("--ip", default="localhost", type=str, help="ip address of the device")
# parser.add_argument("--port", default=5555, type=int, help="ephemeral port number of the server (1024 to 65535)")
# args = parser.parse_args()
# src = args.video
class StreamThread(threading.Thread):
    def __init__(self, ip, port, video="",cameraId=0):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sender = imagezmq.ImageSender(connect_to='tcp://{}:{}'.format(self.ip, self.port))
        self.source_name = socket.gethostname()
        self.isRunning = False
        if video!="":
            src = video
        else:
            src = cameraId
        self.vs = WebcamVideoStream(src=src).start()
        time.sleep(2)
        self.jpeg_quality = 100

    def run(self):
        while self.isRunning:
            frame = self.vs.read()
            t = time.time()
            ret_code, jpg_buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality])
            self.sender.send_image(self.source_name, jpg_buffer)
            print("Stream time: " + str(time.time()-t))
        print("Stopped stream")
        self.vs.stream.release()


# if src == "":
#     src = 0
# print(src)
# vs = WebcamVideoStream(src=src).start()
# time.sleep(2)
# fps = FPS().start()
# # sender = imagezmq.ImageSender("tcp://*:{}".format(args.port))#, REQ_REP=False)
# sender = imagezmq.ImageSender(connect_to='tcp://{}:{}'.format(args.ip, args.port))#, REQ_REP=False)
# source_name = socket.gethostname() # send RPi hostname with each image
# print(source_name)
# # cap = cv2.VideoCapture(args.video)#VideoStream(usePiCamera=True).start()
# # time.sleep(2.0)  # allow camera sensor to warm up

# # loop over some frames...this time using the threaded stream
# try:
#     while True:#fps._numFrames < 100:#args["num_frames"]:
#         frame = vs.read()
#         t = time.time()
#         ret_code, jpg_buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
#         sender.send_image(source_name, jpg_buffer)
#         print("Stream time: " + str(time.time()-t))
# except (KeyboardInterrupt, SystemExit):
#     print('Exit due to keyboard interrupt')
# except Exception as ex:
#     print('Python error with no Exception handler:')
#     print('Traceback error:', ex)
# finally:
#     vs.stop()
#     sender.close()
#     sys.exit()
#     print("Finished stream")