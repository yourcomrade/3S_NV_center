import numpy as np  # Importing numpy for array manipulation
import cv2  # Importing OpenCV for image processing
import matplotlib.pyplot as plt
import time
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK, OPERATION_MODE  # Importing SDK for Thorlabs camera


#Function to capture an image from the camera
def capture_image(camera):
    camera.issue_software_trigger()
    frame = camera.get_pending_frame_or_null()
    if frame is not None:
        image_buffer_copy = np.copy(frame.image_buffer)
        numpy_shaped_image = image_buffer_copy.reshape(camera.image_height_pixels, camera.image_width_pixels)
        return numpy_shaped_image
    else:
        raise Exception("Unable to acquire image")
    
    
#Function to analyze fluorescence intensity
def analyze_fluorescence(image):
    avg_intensity = np.mean(image)
    return avg_intensity

#initialize the camera
with TLCameraSDK() as sdk:  # Using the SDK in a context manager
    available_cameras = sdk.discover_available_cameras()  # Discovering available cameras
    if len(available_cameras) < 1:  # Checking if no cameras are detected
        print("No cameras detected")

    with sdk.open_camera(available_cameras[0]) as camera:  # Opening the first available camera
        camera.exposure_time_us = 10000  # Setting exposure time to 10 ms
        camera.frames_per_trigger_zero_for_unlimited = 0  # Starting camera in continuous mode
        camera.image_poll_timeout_ms = 1000  # Setting polling timeout to 1 second

        camera.arm(2)  # Arming the camera for acquisition

        time_intervals = []
        fluorescence_intensities = []

        # Defining the duration of the experiment
        total_duration = 120
        # Time interval between each measurement
        time_step = 5 

        start_time = time.time()

        while(time.time() - start_time) < total_duration:
            current_time = time.time() - start_time
            image = capture_image(camera) #capture image

            intensity = analyze_fluorescence(image) #analyze fluorescence

            # Store the data
            time_intervals.append(current_time)
            fluorescence_intensities.append(intensity)
            
            print(f"Time: {current_time:.2f} s, Fluorescence Intensity: {intensity}")

            # Wait for the next time step
            time.sleep(time_step)

        # Plot the results
        plt.plot(time_intervals, fluorescence_intensities, marker='o')
        plt.xlabel('Time (s)')
        plt.ylabel('Fluorescence Intensity (a.u.)')
        plt.title('Fluorescence Intensity vs. Time')
        plt.show()

        camera.disarm()

print("Program completed")