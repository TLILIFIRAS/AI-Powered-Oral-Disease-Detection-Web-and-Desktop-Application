import sys
import cv2
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QProgressBar, QStackedWidget, QFrame)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QFont, QColor
import numpy as np
from ultralytics import YOLO

class AnalysisThread(QThread):
    finished = pyqtSignal(object)
    progress = pyqtSignal(int)

    def __init__(self, model, image):
        super().__init__()
        self.model = model
        self.image = image

    def run(self):
        # Simulate progress steps
        for i in range(101):
            self.progress.emit(i)
            self.msleep(20)  # Simulate processing time
        results = self.model(self.image)
        self.finished.emit(results)

class DetectionResult(QWidget):
    def __init__(self, disease, confidence):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Create container frame
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #e0e0e0;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(8)
        
        # Create header with disease name and confidence percentage
        header_layout = QHBoxLayout()
        
        # Disease name
        disease_label = QLabel(disease)
        disease_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 16px;
            }
        """)
        
        # Confidence percentage
        confidence_label = QLabel(f"{int(confidence * 100)}%")
        confidence_label.setStyleSheet("""
            QLabel {
                color: #4361ee;
                font-weight: bold;
                font-size: 16px;
            }
        """)
        
        header_layout.addWidget(disease_label)
        header_layout.addStretch()
        header_layout.addWidget(confidence_label)
        container_layout.addLayout(header_layout)
        
        # Create progress bar
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #f0f0f0;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4361ee, stop:1 #4cc9f0);
                border-radius: 4px;
            }
        """)
        self.progress.setValue(int(confidence * 100))
        container_layout.addWidget(self.progress)
        
        layout.addWidget(container)

class OralDiseaseDetector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Oral Disease Detection System")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QPushButton {
                background-color: #4361ee;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3b55d9;
            }
            QLabel {
                color: #2c3e50;
            }
        """)
        
        # Initialize YOLO model
        self.model = YOLO('best.pt')
        
        # Initialize camera
        self.camera = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        self.create_home_page()
        self.create_image_detection_page()
        self.create_webcam_page()
        
    def create_home_page(self):
        home_page = QWidget()
        layout = QVBoxLayout(home_page)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Title
        title = QLabel("AI-Powered Oral Disease Detection")
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            margin: 20px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Detect oral diseases using advanced AI technology")
        desc.setStyleSheet("font-size: 18px; color: #7f8c8d; margin-bottom: 40px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Buttons container
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setSpacing(20)
        
        # Image Detection Button
        image_btn = self.create_option_button(
            "Image Detection",
            "Upload and analyze dental images",
            "📸",
            lambda: self.stacked_widget.setCurrentIndex(1)
        )
        
        # Webcam Detection Button
        webcam_btn = self.create_option_button(
            "Webcam Detection",
            "Real-time detection using webcam",
            "🎥",
            self.start_webcam
        )
        
        buttons_layout.addWidget(image_btn)
        buttons_layout.addWidget(webcam_btn)
        layout.addWidget(buttons_widget)
        
        self.stacked_widget.addWidget(home_page)
        
    def create_option_button(self, title, description, icon, callback):
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
            QFrame:hover {
                background-color: #f8f9fa;
            }
        """)
        layout = QVBoxLayout(container)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px 0;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #7f8c8d;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        
        container.mousePressEvent = lambda e: callback()
        return container

    def create_image_detection_page(self):
        image_page = QWidget()
        layout = QVBoxLayout(image_page)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Image Analysis")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Main content container
        content = QHBoxLayout()
        
        # Left side - Image display
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        left_layout.addWidget(self.image_label)
        
        # Analysis progress
        self.analysis_progress = QProgressBar()
        self.analysis_progress.setVisible(False)
        self.analysis_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4361ee, stop:1 #4cc9f0);
                border-radius: 3px;
            }
        """)
        left_layout.addWidget(self.analysis_progress)
        
        content.addWidget(left_widget, stretch=2)
        
        # Right side - Results
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        results_title = QLabel("Detection Results")
        results_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        right_layout.addWidget(results_title)
        
        self.results_container = QVBoxLayout()
        results_widget = QWidget()
        results_widget.setLayout(self.results_container)
        right_layout.addWidget(results_widget)
        right_layout.addStretch()
        
        content.addWidget(right_widget, stretch=1)
        layout.addLayout(content)
        
        # Buttons
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        
        select_btn = QPushButton("Select Image")
        select_btn.clicked.connect(self.select_image)
        
        back_btn = QPushButton("Back")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        buttons_layout.addWidget(select_btn)
        buttons_layout.addWidget(back_btn)
        layout.addWidget(buttons_widget)
        
        self.stacked_widget.addWidget(image_page)

    def create_webcam_page(self):
        webcam_page = QWidget()
        layout = QVBoxLayout(webcam_page)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Real-time Detection")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Main content container
        content = QHBoxLayout()
        
        # Webcam display
        self.webcam_label = QLabel()
        self.webcam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.webcam_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        content.addWidget(self.webcam_label, stretch=2)
        
        # Results panel
        results_panel = QWidget()
        results_layout = QVBoxLayout(results_panel)
        
        results_title = QLabel("Live Detection Results")
        results_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        results_layout.addWidget(results_title)
        
        self.webcam_results_container = QVBoxLayout()
        results_widget = QWidget()
        results_widget.setLayout(self.webcam_results_container)
        results_layout.addWidget(results_widget)
        results_layout.addStretch()
        
        content.addWidget(results_panel, stretch=1)
        layout.addLayout(content)
        
        # Stop button
        stop_btn = QPushButton("Stop Webcam")
        stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        stop_btn.clicked.connect(self.stop_webcam)
        layout.addWidget(stop_btn)
        
        self.stacked_widget.addWidget(webcam_page)

    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", 
            "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_name:
            # Show progress bar
            self.analysis_progress.setVisible(True)
            self.analysis_progress.setValue(0)
            
            # Clear previous results
            self.clear_results_container()
            
            # Load image and start analysis thread
            image = cv2.imread(file_name)
            self.display_image(image)
            
            self.analysis_thread = AnalysisThread(self.model, image)
            self.analysis_thread.progress.connect(self.analysis_progress.setValue)
            self.analysis_thread.finished.connect(self.handle_analysis_results)
            self.analysis_thread.start()

    def handle_analysis_results(self, results):
        self.analysis_progress.setVisible(False)
        self.clear_results_container()
        
        # Get the original image
        result = results[0]
        plotted_image = result.orig_img.copy()
        
        # Plot each detection with label
        for box in result.boxes:
            # Get box coordinates
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            
            if confidence >= 0.60:  # 60% confidence threshold
                # Draw rectangle
                cv2.rectangle(plotted_image, 
                             (int(x1), int(y1)), 
                             (int(x2), int(y2)), 
                             (67, 97, 238), 2)  # BGR color format
                
                # Prepare label text
                disease = result.names[class_id]
                label = f"{disease}: {confidence:.2%}"
                
                # Calculate text size and position
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.6
                thickness = 2
                (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)
                
                # Draw label background
                cv2.rectangle(plotted_image, 
                             (int(x1), int(y2)), 
                             (int(x1 + text_width), int(y2 + text_height + baseline)), 
                             (67, 97, 238), -1)
                
                # Draw label text
                cv2.putText(plotted_image, label, 
                           (int(x1), int(y2 + text_height)), 
                           font, font_scale, (255, 255, 255), thickness)
        
        # Display the image with detections and labels
        self.display_image(plotted_image)
        
        # Update results panel
        for r in results[0].boxes.data:
            confidence = float(r[4])
            if confidence >= 0.60:
                class_id = int(r[5])
                disease = results[0].names[class_id]
                result_widget = DetectionResult(disease, confidence)
                self.results_container.addWidget(result_widget)
        
        # Add stretch to push results to the top
        self.results_container.addStretch()

    def clear_results_container(self):
        while self.results_container.count():
            item = self.results_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def display_image(self, image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, 
                        QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio
        )
        self.image_label.setPixmap(scaled_pixmap)

    def start_webcam(self):
        self.camera = cv2.VideoCapture(0)
        self.stacked_widget.setCurrentIndex(2)
        self.timer.start(30)

    def stop_webcam(self):
        self.timer.stop()
        if self.camera is not None:
            self.camera.release()
        self.camera = None
        self.stacked_widget.setCurrentIndex(0)

    def update_frame(self):
        if self.camera is not None:
            ret, frame = self.camera.read()
            if ret:
                results = self.model(frame)
                result_frame = results[0].plot()
                
                # Update webcam display
                height, width, channel = result_frame.shape
                bytes_per_line = 3 * width
                q_image = QImage(
                    result_frame.data, width, height, 
                    bytes_per_line, QImage.Format.Format_RGB888
                )
                pixmap = QPixmap.fromImage(q_image)
                scaled_pixmap = pixmap.scaled(
                    self.webcam_label.size(), 
                    Qt.AspectRatioMode.KeepAspectRatio
                )
                self.webcam_label.setPixmap(scaled_pixmap)
                
                # Update results
                self.update_webcam_results(results)

    def update_webcam_results(self, results):
        # Clear previous results
        while self.webcam_results_container.count():
            item = self.webcam_results_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add new results
        for r in results[0].boxes.data:
            confidence = float(r[4])
            if confidence >= 0.60:
                class_id = int(r[5])
                disease = results[0].names[class_id]
                result_widget = DetectionResult(disease, confidence)
                self.webcam_results_container.addWidget(result_widget)
        
        # Add stretch to push results to the top
        self.webcam_results_container.addStretch()

    def closeEvent(self, event):
        self.stop_webcam()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = OralDiseaseDetector()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()