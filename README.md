# Hand detection DMX controller

Uses a webcam to detect your hand and set the value of hardcoded DMX channels to a value between 0 (hand at bottom of frame) and 255 (hand at top of frame).

Implementation is for the [Eurolite USB-DMX512 PRO Cable Interface](https://www.thomann.de/de/eurolite_usb_dmx512_pro_cable_interface.htm), not sure if it works for any other USB DMX Controller. Under Windows you need to make sure the driver for this controller is libusb. Use [Zadig](https://zadig.akeo.ie/) to install the driver for the device.

To use it:
- create a venv (e.g. `python -m venv venv-dmx`)
- activate a venv (e.g. `source venv-dmx/Scripts/activate` [Windows] or `source venv-dmx/bin/activate` [Linux])
- `pip install -r requirements.txt`
- `python hand_detection_dmx_control.py`
- `hand_detection_dmx_control.py` contains several settings at the top of the file that you can edit. Most importantly the video capture device index. To find the correct index for your webcam, use `python print_video_device_infos.py`
