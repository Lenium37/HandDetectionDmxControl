import cv2
import mediapipe as mp
from dmx_device_eurolite_pro import DmxDeviceEurolitePro
import tkinter as tk
from threading import Thread

SHOW_VIDEO = False # doesn't work anymore, don't know why :(
VIDEO_CAPTURE_DEVICE_INDEX = 0 # find out the index of available cameras by using print_video_device_infos.py
NUM_HAND_FEATURES = 21 # mediapipe returns 21 landmarks per hand
MIN_Y = 0.85 # inverted y axis
MAX_Y = 0 # inverted y axis
MIN_DMX = 0 # if a hand is detected at the bottom of the frame
MAX_DMX = 255 # if a hand is detected at the top of the frame
INITIAL_DIMMER_VALUE = 255 # this value is set to the channels at the beginning of the program

DYNAMIC_DIMMER_CHANNELS = [3, 8, 13, 18, 23, 28, 33, 38] # these are the blue channels in reality because no dimmer exists

CONSTANT_VALUE_CHANNELS = [] # if you want to set some channels to static values
CONSTANT_VALUE = 255 # the value that is set for all channels in CONSTANT_VALUE_CHANNELS


class HandDetectionDmxControl:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand detection dimmer controller")

        # Create an instance of DmxDeviceEurolitePro
        self.dmx_device = DmxDeviceEurolitePro()

        # init Mediapipe stuff
        self.mp_hands = mp.solutions.hands.Hands(min_detection_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        self.current_dimmer_value = INITIAL_DIMMER_VALUE

        # Stop button
        self.stop_button = tk.Button(self.root, text="Close hand detection", command=self.stop_webcam_loop)
        self.stop_button.grid(row=1, column=0, columnspan=2, pady=10)

        # init DMX device
        self.start_dmx_device()

        # start loop of sending DMX values
        Thread(target=self.webcam_loop).start()

    def stop_webcam_loop(self):
        # stop detection
        self.webcam.release()
        cv2.destroyAllWindows()

        # set all channels to 0
        for dim_channel in DYNAMIC_DIMMER_CHANNELS:
            self.update_dmx_value(dim_channel, 0)

        for dim_channel in CONSTANT_VALUE_CHANNELS:
            self.update_dmx_value(dim_channel, 0)
        self.send_dmx_values()

        # close everything
        self.stop_dmx_device()
        self.root.quit()

    def webcam_loop(self):
        self.webcam = cv2.VideoCapture(VIDEO_CAPTURE_DEVICE_INDEX)
        while self.webcam.isOpened():
            success, img = self.webcam.read()
            if not success:
                print('Failed to read video frame')
                continue

            # apply hand tracking model
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.mp_hands.process(img)

            # get detected hands and average Y
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    total_y = sum(landmark.y for landmark in hand_landmarks.landmark)
                    avg_y = total_y / NUM_HAND_FEATURES
                    self.current_dimmer_value = self.map_y_to_dmx(avg_y, MIN_Y, MAX_Y, MIN_DMX, MAX_DMX)

            for dim_channel in DYNAMIC_DIMMER_CHANNELS:
                self.update_dmx_value(dim_channel, self.current_dimmer_value)

            for dim_channel in CONSTANT_VALUE_CHANNELS:
                self.update_dmx_value(dim_channel, CONSTANT_VALUE)
            self.send_dmx_values()

            if SHOW_VIDEO:
                cv2.imshow('Hand detection', img)

        self.webcam.release()
        cv2.destroyAllWindows()

    def map_y_to_dmx(self, value, min_y, max_y, min_dmx, max_dmx):
        # Figure out how 'wide' each range is
        leftSpan = max_y - min_y
        rightSpan = max_dmx - min_dmx

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - min_y) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        result = int(min_dmx + (valueScaled * rightSpan))
        if result < 0:
            result = 0
        elif result > 255:
            result = 255
        return result

    def send_dmx_values(self):
        self.dmx_device.write_complete_data()

    def update_dmx_value(self, channel, value):
        # Update the DMX value for the specified channel
        self.dmx_device.update_channel_value(channel, int(value))

    def start_dmx_device(self):
        # Start the DMX device in a separate thread
        Thread(target=self.start_dmx_device_thread).start()

    def start_dmx_device_thread(self):
        # Start the DMX device
        try:
            self.dmx_device.start_device()
            print("DMX device started.")
            self.dmx_device.write_complete_data()
        except Exception as e:
            print(f"Error starting DMX device: {e}")

    def stop_dmx_device(self):
        # Stop the DMX device
        try:
            self.dmx_device.stop_device()
            print("DMX device stopped.")
        except Exception as e:
            print(f"Error stopping DMX device: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HandDetectionDmxControl(root)
    root.mainloop()  # Run the main loop for GUI and check for key presses
