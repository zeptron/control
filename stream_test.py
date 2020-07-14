# Usage example:  python counting_people.py --video=car.mp4 --line=horizontal --classId=2,5,7 --ip=0.0.0.0 --port=8000 --stream_port=5555 --no_process=1 --device_FPS=30
#python counting_people.py --video=TownCentreXVID.mp4 --line=horizontal --classId=0,1 --ip=0.0.0.0 --port=8000 --stream_port=5555 --no_process=1 --device_FPS=30
import cv2 as cv
import argparse
import sys
import time
import numpy as np
import os.path
from datetime import datetime
from flask import Response
from flask import Flask
from flask import render_template
import threading
import multiprocessing
import imagezmq

parser = argparse.ArgumentParser(description='Object Detection using YOLO in OPENCV')

parser.add_argument('--video', default="", help='Path to video file.')
parser.add_argument('--classId',type=str, help='ClassID to count')
parser.add_argument('--line', type=str, help='Horizontal or Vertical')
parser.add_argument('--jsonName', type=str, default="log.json", help='Log JSON file name')
parser.add_argument("--ip", default="0.0.0.0", type=str, help="ip address of the device")
parser.add_argument("--port", default=8888, type=int, help="ephemeral port number of the server (1024 to 65535)")
parser.add_argument("--stream_port", default=5555, type=int, help="Port to stream from camera")
parser.add_argument("--receiver_ip", default="127.0.0.1", type=str, help="Rpi ip address")
parser.add_argument("--no_process", default=1, type=int, help="Number or process, it's should below 6")
parser.add_argument("--device_FPS", default=30, type=int, help="FPS of input source")
args = parser.parse_args()


isRunning = True
streamFrame = None
frame = None
lock = threading.Lock()
# initialize a flask object
app = Flask(__name__)
@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")


@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")


class VideoStreamSubscriber:

    def __init__(self, port):
        # self.hostname = hostname
        self.port = port
        self._stop = False
        self._data_ready = threading.Event()
        self._thread = threading.Thread(target=self._run, args=())
        self._thread.daemon = True
        self._thread.start()

    def receive(self, timeout=200.0):
        flag = self._data_ready.wait(timeout=timeout)
        if not flag:
            raise TimeoutError(
                "Timeout while reading from subscriber{}".format(self.port))
        self._data_ready.clear()
        return self._data

    def _run(self):
        stream_port ='tcp://*:{}'.format(self.port)
        receiver = imagezmq.ImageHub(stream_port)# imagezmq.ImageHub("tcp://{}:{}".format(self.hostname, self.port), REQ_REP=False)
        while not self._stop:
            self._data = receiver.recv_jpg()
            self._data_ready.set()
            receiver.send_reply(b'OK')
        receiver.close()

    def close(self):
        self._stop = True

# Simulating heavy processing load
def limit_to_2_fps():
    sleep(0.5)


def stream_thread():
    # Process inputs
    print("STREAM TO WEB")
    global streamFrame, lock
    # stream_port ='tcp://*:{}'.format(args.stream_port)
    # image_hub = imagezmq.ImageHub(stream_port)
    hostname = args.receiver_ip# "192.168.1.135"  # Use to receive from localhost
    # hostname = "192.168.86.38"  # Use to receive from other computer
    # port = 5555
    port =args.stream_port
    receiver = VideoStreamSubscriber(port)
    # winName = 'Deep learning object detection in OpenCV'
    # cv.namedWindow(winName, cv.WINDOW_NORMAL)

    outputFile = "yolo_out_py.avi"
    cap = None
    isRunning = True
    if args.video != "":
        if os.path.isfile(args.video):
            print("Process on video: {}".format(args.video))
            cap = cv.VideoCapture(args.video)
            outputFile = args.video[:-4]+'_yolo_out_py.avi'
            isRunning = True
        else:
            print("Video path not exist. Please check: {}".format(args.video))
            isRunning = False
    # Get the video writer initialized to save the output video
    if cap != None:
        vid_writer = cv.VideoWriter(outputFile, cv.VideoWriter_fourcc('M','J','P','G'), 30, (round(cap.get(cv.CAP_PROP_FRAME_WIDTH)),round(cap.get(cv.CAP_PROP_FRAME_HEIGHT))))

    try:
        while isRunning:
            # get frame from the video
            # hasFrame, frame = cap.read()
            t = time.time()
            if args.video != "":    #using source as video
                hasFrame, frame = cap.read()
                if not hasFrame:
                    print("Done processing !!!")
                    print("Output file is stored as ", outputFile)
                    #cv.waitKey(3000)
                    # Release device
                    cap.release()
                    break
            else:
                tt = time.time()
                # source_name, frame = image_hub.recv_image()
                # image_hub.send_reply(b'OK')
                msg, frame = receiver.receive()
                frame = cv.imdecode(np.frombuffer(frame, dtype='uint8'), -1)
                
                print("Receive time: " + str(time.time()-tt))

            FPS = "Stream time: {}".format((time.time()-t))
            cv.putText(frame, FPS, (20,20), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
            

            # Write the frame with the detection boxes
            # if cap != None:
            #     vid_writer.write(frame.astype(np.uint8))
            with lock:
                streamFrame = frame.copy()
            # cv.imshow(winName, frame)
    except (KeyboardInterrupt, SystemExit):
        print('Exit due to keyboard interrupt')
    finally:
        # receiver.close()
        sys.exit()
        print("Finish stream process.")

def generate():
	# grab global references to the output frame and lock variables
	global streamFrame, lock

	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if streamFrame is None:
				continue

			# encode the frame in JPEG format
			(flag, encodedImage) = cv.imencode(".jpg", streamFrame)

			# ensure the frame was successfully encoded
			if not flag:
				continue

		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

# check to see if this is the main thread of execution
if __name__ == '__main__':
    stream_thread = threading.Thread(target=stream_thread)
    stream_thread.daemon = True
    stream_thread.start()
    # start the flask app
    app.run(host=args.ip, port=args.port, debug=True,threaded=True, use_reloader=False)
isRunning = False

