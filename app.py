from flask import Flask, render_template, request, redirect, url_for, Response
import os
from ultralytics import YOLO
import cv2
from PIL import Image
import numpy as np

app = Flask(__name__)

# Configure upload and result folders
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Load YOLO model
model = YOLO('best.pt')

# Global variable for webcam
camera = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
    return camera

def generate_frames():
    camera = get_camera()
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Run YOLO detection on frame
            results = model(frame)
            
            # Draw the results on the frame
            annotated_frame = results[0].plot()
            
            # Convert to jpg format
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            frame = buffer.tobytes()
            
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/webcam')
def webcam():
    return render_template('webcam.html')

@app.route('/stop_webcam')
def stop_webcam():
    global camera
    if camera:
        camera.release()
        camera = None
    return redirect(url_for('upload_file'))

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/detect', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Save uploaded image
            upload_path = os.path.join(UPLOAD_FOLDER, 'input_image.jpg')
            file.save(upload_path)
            
            # Perform YOLO detection
            results = model(upload_path)
            
            # Save the result image
            result_path = os.path.join(RESULT_FOLDER, 'result_image.jpg')
            
            # Plot results and save
            res_plotted = results[0].plot()
            cv2.imwrite(result_path, res_plotted)
            
            return redirect(url_for('show_result'))
    
    return render_template('index.html')

@app.route('/result')
def show_result():
    results = model(os.path.join(UPLOAD_FOLDER, 'input_image.jpg'))
    
    # Extract detection results
    detections = []
    for r in results[0].boxes.data:
        confidence = float(r[4])
        class_id = int(r[5])
        disease = results[0].names[class_id]
        detections.append({
            'disease': disease,
            'confidence': round(confidence * 100, 2)  # Convert to percentage and round to 2 decimal places
        })
    
    return render_template('result.html', detections=detections)

@app.teardown_appcontext
def cleanup(exception=None):
    global camera
    if camera:
        camera.release()

if __name__ == '__main__':
    app.run(debug=True) 