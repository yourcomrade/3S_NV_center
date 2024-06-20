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

# Function to find the ROI where the light is hitting the lens
def find_roi(image):
    # Convert the image to grayscale if it's not already
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Ensure the grayscale image is of type CV_8UC1
    gray = gray.astype(np.uint8)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply adaptive threshold to get a binary image
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If no contours are found, return a default ROI
    if not contours:
        return (0, 0, image.shape[1], image.shape[0])

    # Find the largest contour
    largest_contour = max(contours, key=cv2.contourArea)

    # Get the bounding box of the largest contour
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    return (x, y, w, h)

# Function to analyze fluorescence intensity in the ROI
def analyze_fluorescence(image, roi):
    x, y, w, h = roi
    cropped_image = image[y:y+h, x:x+w]
    avg_intensity = np.mean(cropped_image)
    return avg_intensity

# Initialize the camera
with TLCameraSDK() as sdk:  # Using the SDK in a context manager
    available_cameras = sdk.discover_available_cameras()  # Discovering available cameras
    if len(available_cameras) < 1:  # Checking if no cameras are detected
        print("No cameras detected")
        exit()

    with sdk.open_camera(available_cameras[0]) as camera:  # Opening the first available camera
        camera.exposure_time_us = 40  # Increase exposure time to 50 ms to capture more light
        camera.frames_per_trigger_zero_for_unlimited = 0  # Starting camera in continuous mode
        camera.image_poll_timeout_ms = 1000  # Setting polling timeout to 1 second

        camera.arm(2)  # Arming the camera for acquisition

        time_intervals = []
        fluorescence_intensities = []

        # Defining the duration of the experiment
        total_duration = 600
        # Time interval between each measurement
        time_step = 1

        # Interactive mode for the plotting
        plt.ion()  # Turn on interactive mode
        fig, ax = plt.subplots()
        line, = ax.plot(time_intervals, fluorescence_intensities, marker='o')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Fluorescence Intensity (a.u.)')
        ax.set_title('Fluorescence Intensity vs. Time')
        start_time = time.time()

        # Open a CSV file to write the data
        with open('fluorescence_data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time (s)', 'Fluorescence Intensity (a.u.)'])  # Write the header

            while (time.time() - start_time) < total_duration:
                current_time = time.time() - start_time
                image = capture_image(camera)  # Capture image

                roi = find_roi(image)  # Detect the ROI
                intensity = analyze_fluorescence(image, roi)  # Analyze fluorescence in ROI

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

                # Save the image with the ROI marked
                x, y, w, h = roi
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                filename = f'captured_image_{int(current_time)}.png'
                cv2.imwrite(filename, image)

                # Wait for the next time step
                time.sleep(time_step)

        plt.ioff()  # Turn off interactive mode
        plt.show()
        camera.disarm()

print("Program completed")
