import numpy as np  # Importing numpy for array manipulation
import cv2  # Importing OpenCV for image processing
import os
import matplotlib.pyplot as plt
import time
import csv  # Importing csv for writing to CSV files
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK, OPERATION_MODE  # Importing SDK for Thorlabs camera
os.add_dll_directory(r"C:\Program Files\Thorlabs\Scientific Imaging\Scientific Camera Support\Scientific_Camera_Interfaces\Scientific Camera Interfaces\SDK\Python Toolkit\dlls\64_lib")

# Function to capture an image from the camera
def capture_image(camera):
    camera.issue_software_trigger()
    frame = camera.get_pending_frame_or_null()
    if frame is not None:
        image_buffer_copy = np.copy(frame.image_buffer)
        numpy_shaped_image = image_buffer_copy.reshape(camera.image_height_pixels, camera.image_width_pixels)
        return numpy_shaped_image
    else:
        raise Exception("Unable to acquire image")
    
# Function to analyze fluorescence intensity
def analyze_fluorescence(image):
    avg_intensity = np.mean(image)
    return avg_intensity

# Initialize the camera
with TLCameraSDK() as sdk:  # Using the SDK in a context manager
    available_cameras = sdk.discover_available_cameras()  # Discovering available cameras
    if len(available_cameras) < 1:  # Checking if no cameras are detected
        print("No cameras detected")

    with sdk.open_camera(available_cameras[0]) as camera:  # Opening the first available camera
        camera.exposure_time_us = 40 # Setting exposure time to 10 ms
        camera.frames_per_trigger_zero_for_unlimited = 0  # Starting camera in continuous mode
        camera.image_poll_timeout_ms = 1000  # Setting polling timeout to 1 second

        camera.arm(2)  # Arming the camera for acquisition

        time_intervals = []
        fluorescence_intensities = []

        # Defining the duration of the experiment
        total_duration = 300
        # Time interval between each measurement
        time_step = 0.1

        # Interactive mode for the plotting
        plt.ion()  # Turn on interactive mode
        fig, ax = plt.subplots()
        line, = ax.plot(time_intervals, fluorescence_intensities, marker='o')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Fluorescence Intensity (a.u.)')
        ax.set_title('Fluorescence Intensity vs. Time')
        start_time = time.time()

        # Open a CSV file to write the data
        with open('fluorescence_data_4.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time (s)', 'Fluorescence Intensity (a.u.)'])  # Write the header

            while (time.time() - start_time) < total_duration:
                current_time = time.time() - start_time
                image = capture_image(camera)  # Capture image

                intensity = analyze_fluorescence(image)  # Analyze fluorescence

                # Store the data
                time_intervals.append(current_time)
                fluorescence_intensities.append(intensity)
                
                print(f"Time: {current_time:.2f} s, Fluorescence Intensity: {intensity}")

                # Write the data to the CSV file
                writer.writerow([current_time, intensity])

                # Plot the results
                # Update the plot
                line.set_xdata(time_intervals)
                line.set_ydata(fluorescence_intensities)
                ax.relim()
                ax.autoscale_view()
                plt.draw()
                plt.pause(0.01)  # Pause to allow the plot to update

                # Display the image using OpenCV
                cv2.imshow('Captured Image', image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                # Wait for the next time step
                time.sleep(time_step)

        plt.ioff()  # Turn off interactive mode
        plt.show()
        cv2.destroyAllWindows()
        camera.disarm()

print("Program completed")
