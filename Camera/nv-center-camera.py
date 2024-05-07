import numpy as np  # Importing numpy for array manipulation
import cv2  # Importing OpenCV for image processing
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK, OPERATION_MODE  # Importing SDK for Thorlabs camera

with TLCameraSDK() as sdk:  # Using the SDK in a context manager
    available_cameras = sdk.discover_available_cameras()  # Discovering available cameras
    if len(available_cameras) < 1:  # Checking if no cameras are detected
        print("No cameras detected")

    with sdk.open_camera(available_cameras[0]) as camera:  # Opening the first available camera
        camera.exposure_time_us = 10000  # Setting exposure time to 10 ms
        camera.frames_per_trigger_zero_for_unlimited = 0  # Starting camera in continuous mode
        camera.image_poll_timeout_ms = 1000  # Setting polling timeout to 1 second

        camera.arm(2)  # Arming the camera for acquisition

        camera.issue_software_trigger()  # Issuing a software trigger to capture an image

        frame = camera.get_pending_frame_or_null()  # Getting the pending frame from the camera
        if frame is not None:  # Checking if a frame is received
            print("frame #{} received!".format(frame.frame_count))  # Printing frame count
            frame.image_buffer  # Accessing the image buffer of the frame
            image_buffer_copy = np.copy(frame.image_buffer)  # Creating a copy of the image buffer
            numpy_shaped_image = image_buffer_copy.reshape(camera.image_height_pixels, camera.image_width_pixels)  # Reshaping the image buffer
            nd_image_array = np.full((camera.image_height_pixels, camera.image_width_pixels, 3), 0, dtype=np.uint8)  # Creating an empty image array
            nd_image_array[:,:,0] = numpy_shaped_image  # Assigning the image data to the blue channel
            nd_image_array[:,:,1] = numpy_shaped_image  # Assigning the image data to the green channel
            nd_image_array[:,:,2] = numpy_shaped_image  # Assigning the image data to the red channel

            # Count the number of pixels that is captured by the camera
            # check for the intensity of the laser by difference in continous frames captured??? Check with Tjeerd.
            pixel_count = camera.image_height_pixels * camera.image_width_pixels
            print("Number of pixels: ", pixel_count);
            
            cv2.imshow("Image From TSI Cam", nd_image_array)  # Displaying the image using OpenCV
            cv2.imwrite(f"frame.png", frame.image_buffer)  # Saving the image to a file
        else:
            print("Unable to acquire image, program exiting...")  # Printing error message
            exit()  # Exiting the program
            
        cv2.waitKey(0)  # Waiting for a key press
        camera.disarm()  # Disarming the camera after acquisition

# The context manager takes care of disposing resources properly.

print("program completed")  # Printing completion message
