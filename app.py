# import flask, requests
from flask import Flask, render_template, request
import stream_camera_v3
import argparse

parser = argparse.ArgumentParser(description='Object Detection using YOLO in OPENCV')
parser.add_argument("--port", default=5000, type=int, help="Port to start app on")
args = parser.parse_args()

# Create the application.
APP = Flask(__name__)
class vars:
    stream = None

@APP.route('/', methods=['GET', 'POST'])
def index():
    """ Displays the index page accessible at '/'
    """
    print("REQUEST METHOD: " , request.method)
    if request.method == "POST":
        print("request.form.get: ", request.form.get("btn_start"))
        if request.form.get("btn_start") == "Start":
            IP = request.form.get("IP")
            PORT = request.form.get("Port")
            VIDEO=request.form.get("Video")
            print("IP: {}, PORT: {}".format(IP, PORT))
            print("VIDEO: {}".format(VIDEO))
            if PORT != "" and IP != "":
                vars.stream = stream_camera_v3.StreamThread(IP, PORT, VIDEO)
                vars.stream.isRunning = True
                vars.stream.start()
            else:
                print("Invalid IP/PORT")
        elif request.form.get("btn_stop") == "Stop":
            print("Stop click")
            if vars.stream != None:
                vars.stream.isRunning = False
        else:
            print("ELSE")


    return render_template('index.html')

# @APP.route('/process', methods=['POST'])
# def process():
#     if requests.method == "GET":
#         if requests.form["btn_start"] == "Start":
#             print("Start press")
#         else:
#             print("Else")
#     print(ip)

if __name__ == '__main__':
    APP.debug=True
    APP.run(host=('0.0.0.0'), port=('{}'.format(args.port)))