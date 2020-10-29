# Install Zeptron streaming & UI to start / stop stream

This repository installs the Zeptron streaming service on the Raspberry Pi as well as a user-friendly interface to start, stop, and monitor streams

## Installation

`git clone https://github.com/zeptron/control`

`cd control`

`pip install -r requirements.txt`

It is also recommended to set up the Pi as a bridged access point

You can view [instructions on doing that on the official Raspberry Pi website](https://www.raspberrypi.org/documentation/configuration/wireless/access-point-bridged.md#:~:text=The%20Raspberry%20Pi%20can%20be,up%20a%20routed%20access%20point)

However, set it up in the inverse with wlan0 as the internet connection which provides internet access to eth0

## Usage

Once you have done this you can use the package as such 

`cd control`

`python3 app.py`

Optionally, if you're running multiple streams on one pi, you can set a port number as such 

`screen`

`python3 app.py --port 5001`

`Ctrl A + D`
 
`screen`

`python3 app.py --port 5002`

You can access the UI at {ip}:{port}

  
