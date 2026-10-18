import cv2
import numpy as np
import requests





def getImage(local_server_path):
    e = None
    frame = None
    try:
        # Send a GET request (with a timeout so your script doesn't hang indefinitely)
        response = requests.get(local_server_path, timeout=5)

        # Check if the request was successful (HTTP Status 200)
        if response.status_code == 200:

            # Load directly into OpenCV for your vision pipeline
            # Convert response bytes to a NumPy array
            image_array = np.asarray(bytearray(response.content), dtype=np.uint8)

            # Decode the array into an OpenCV image frame
            frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            if frame is not None:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)  
                return frame, e
            else:
                e = "⚠️ Failed to decode image bytes into an OpenCV frame."
                return frame, e

        else:
            e = f"❌ Server returned status code: {response.status_code}"
            return frame, e

    except requests.exceptions.RequestException as e:
        return frame, (f"❌ Connection error: {e}")

if __name__ == "__main__":
    getImage(local_server_path = "http://192.168.1.15:8080/photo.jpg")