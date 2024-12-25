import os
import numpy as np
import cv2
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QFileDialog, QLabel, QSlider, QComboBox, QScrollArea, QTabWidget, 
                             QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont

class TikTokVideoTool(QWidget):
    def __init__(self):
        super().__init__()

        # Initial UI setup
        self.setWindowTitle("TikTok Video Unique Tool")
        self.setGeometry(100, 100, 1000, 600)  # Increase width for preview

        # Create a tab widget to separate the preview and settings
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)  # Tabs on the top

        # Create the Preview Tab
        self.preview_tab = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_tab)

        self.preview_label = QLabel("Video Preview will appear here")
        self.preview_label.setAlignment(Qt.AlignCenter)  # Center the preview label
        self.preview_layout.addWidget(self.preview_label)

        # Play/Pause Button
        self.play_pause_btn = QPushButton("Play")
        self.play_pause_btn.clicked.connect(self.toggle_playback)
        self.preview_layout.addWidget(self.play_pause_btn)

        # Create the Settings Tab
        self.settings_tab = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_tab)

        # Set custom font (Montserrat)
        font = QFont("Montserrat", 10)
        self.setFont(font)

        # Theme Selector
        self.theme_combobox = QComboBox()
        self.theme_combobox.addItems(["Black", "White", "Grey", "Modern Black & White"])
        self.theme_combobox.currentIndexChanged.connect(self.change_theme)
        self.settings_layout.addWidget(self.theme_combobox)

        # Load Video Button
        self.load_video_btn = QPushButton("Load Video")
        self.load_video_btn.clicked.connect(self.load_video)
        self.settings_layout.addWidget(self.load_video_btn)

        # Video Path Label
        self.video_path_label = QLabel("No video loaded")
        self.settings_layout.addWidget(self.video_path_label)

        # Color Correction Slider (CC)
        self.cc_slider = QSlider(Qt.Horizontal)
        self.cc_slider.setMinimum(0)
        self.cc_slider.setMaximum(100)
        self.cc_slider.setValue(50)
        self.cc_slider.setTickInterval(1)
        self.cc_slider.setTickPosition(QSlider.TicksBelow)
        self.cc_slider.valueChanged.connect(self.update_video_preview)
        self.settings_layout.addWidget(QLabel("Adjust Color Correction (CC):"))
        self.settings_layout.addWidget(self.cc_slider)

        # Brightness and Contrast Controls
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setMinimum(-100)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.setTickInterval(1)
        self.brightness_slider.valueChanged.connect(self.update_video_preview)
        self.settings_layout.addWidget(QLabel("Adjust Brightness:"))
        self.settings_layout.addWidget(self.brightness_slider)

        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setMinimum(-100)
        self.contrast_slider.setMaximum(100)
        self.contrast_slider.setValue(0)
        self.contrast_slider.setTickInterval(1)
        self.contrast_slider.valueChanged.connect(self.update_video_preview)
        self.settings_layout.addWidget(QLabel("Adjust Contrast:"))
        self.settings_layout.addWidget(self.contrast_slider)

        # Hue Slider
        self.hue_slider = QSlider(Qt.Horizontal)
        self.hue_slider.setMinimum(0)
        self.hue_slider.setMaximum(360)
        self.hue_slider.setValue(0)
        self.hue_slider.setTickInterval(1)
        self.hue_slider.setTickPosition(QSlider.TicksBelow)
        self.hue_slider.valueChanged.connect(self.update_video_preview)
        self.settings_layout.addWidget(QLabel("Adjust Hue:"))
        self.settings_layout.addWidget(self.hue_slider)

        # Additional video editing controls
        # Sharpness Slider
        self.sharpness_slider = QSlider(Qt.Horizontal)
        self.sharpness_slider.setMinimum(-100)
        self.sharpness_slider.setMaximum(100)
        self.sharpness_slider.setValue(0)
        self.sharpness_slider.setTickInterval(1)
        self.sharpness_slider.valueChanged.connect(self.update_video_preview)
        self.settings_layout.addWidget(QLabel("Adjust Sharpness:"))
        self.settings_layout.addWidget(self.sharpness_slider)

        # Saturation Slider
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setMinimum(-100)
        self.saturation_slider.setMaximum(100)
        self.saturation_slider.setValue(0)
        self.saturation_slider.setTickInterval(1)
        self.saturation_slider.valueChanged.connect(self.update_video_preview)
        self.settings_layout.addWidget(QLabel("Adjust Saturation:"))
        self.settings_layout.addWidget(self.saturation_slider)

        # Rotate Slider
        self.rotate_slider = QSlider(Qt.Horizontal)
        self.rotate_slider.setMinimum(0)
        self.rotate_slider.setMaximum(360)
        self.rotate_slider.setValue(0)
        self.rotate_slider.setTickInterval(1)
        self.rotate_slider.valueChanged.connect(self.update_video_preview)
        self.settings_layout.addWidget(QLabel("Rotate Video:"))
        self.settings_layout.addWidget(self.rotate_slider)

        # Export Button
        self.export_btn = QPushButton("Export Video")
        self.export_btn.clicked.connect(self.export_video)
        self.settings_layout.addWidget(self.export_btn)

        # Set initial theme
        self.current_theme = "Black"
        self.apply_theme(self.current_theme)

        # Add the tabs to the tab widget
        self.tab_widget.addTab(self.preview_tab, "Preview")
        self.tab_widget.addTab(self.settings_tab, "Settings")

        # Main layout setup with horizontal scrollbar
        self.main_layout = QHBoxLayout(self)
        self.main_layout.addWidget(self.tab_widget)

        # Scroll Area for the settings tab
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.settings_tab)
        self.main_layout.addWidget(self.scroll_area)

        self.setLayout(self.main_layout)

        # Internal state
        self.video_path = None
        self.video_frame = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_preview)
        self.is_playing = False  # Control the playback state

        # Show creator popup when the app starts
        self.show_creator_popup()

    def load_video(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.mov *.avi)")
        if file_path:
            self.video_path = file_path
            self.video_path_label.setText(f"Loaded: {os.path.basename(file_path)}")
            self.load_video_preview()

    def toggle_playback(self):
        """ Toggle play/pause of the video preview """
        if self.is_playing:
            self.play_pause_btn.setText("Play")
            self.timer.stop()
        else:
            self.play_pause_btn.setText("Pause")
            self.timer.start(50)  # Update preview every 50 ms
        self.is_playing = not self.is_playing

    def update_video_preview(self):
        """ Update the preview video frame based on current settings """
        if self.video_frame is not None:
            cc_value = self.cc_slider.value() / 100
            brightness = self.brightness_slider.value() / 100.0
            contrast = self.contrast_slider.value() / 100.0
            hue_value = self.hue_slider.value()
            sharpness = self.sharpness_slider.value() / 100.0
            saturation = self.saturation_slider.value() / 100.0
            rotate_angle = self.rotate_slider.value()

            frame = self.apply_color_correction(self.video_frame, cc_value)
            frame = cv2.convertScaleAbs(frame, alpha=1 + contrast, beta=brightness * 255)
            frame = self.apply_hue(frame, hue_value)
            frame = self.apply_sharpness(frame, sharpness)
            frame = self.apply_saturation(frame, saturation)
            frame = self.apply_rotation(frame, rotate_angle)

            # Scale the video frame to half its original size
            frame = cv2.resize(frame, (frame.shape[1] // 2, frame.shape[0] // 2))

            # Convert to QPixmap and update QLabel
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            qimage = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.preview_label.setPixmap(QPixmap.fromImage(qimage))

    def apply_color_correction(self, frame, cc_value):
        """ Apply color correction """
        return cv2.convertScaleAbs(frame, alpha=1.0, beta=cc_value)

    def apply_hue(self, frame, hue_value):
        """ Apply hue adjustment """
        hue_value = hue_value % 180  # Ensure the hue value is within the valid range (0-179)
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv_frame[..., 0] = (hsv_frame[..., 0] + hue_value) % 180
        return cv2.cvtColor(hsv_frame, cv2.COLOR_HSV2BGR)

    def apply_sharpness(self, frame, sharpness_value):
        """ Apply sharpness adjustment """
        kernel = np.array([[0, -1, 0], [-1, 5+sharpness_value, -1], [0, -1, 0]])
        return cv2.filter2D(frame, -1, kernel)

    def apply_saturation(self, frame, saturation_value):
        """ Apply saturation adjustment """
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv_frame[..., 1] = np.clip(hsv_frame[..., 1] * (1 + saturation_value), 0, 255)
        return cv2.cvtColor(hsv_frame, cv2.COLOR_HSV2BGR)

    def apply_rotation(self, frame, angle):
        """ Apply rotation to the video frame """
        height, width = frame.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(frame, rotation_matrix, (width, height))

    def load_video_preview(self):
        """ Load the first frame of the video to be used as preview """
        video = cv2.VideoCapture(self.video_path)
        ret, frame = video.read()
        if ret:
            self.video_frame = frame
            self.update_video_preview()  # Immediately show the first frame
        video.release()

    def apply_theme(self, theme):
        """ Apply selected theme to the UI """
        if theme == "Black":
            self.setStyleSheet("background-color: #2E2E2E; color: white;")
        elif theme == "White":
            self.setStyleSheet("background-color: white; color: black;")
        elif theme == "Grey":
            self.setStyleSheet("background-color: #B0B0B0; color: black;")
        elif theme == "Modern Black & White":
            self.setStyleSheet("background-color: #111111; color: #EEEEEE;")

    def change_theme(self):
        """ Handle theme change """
        self.current_theme = self.theme_combobox.currentText()
        self.apply_theme(self.current_theme)

    def export_video(self):
        if not self.video_path:
            self.video_path_label.setText("No video loaded! Please load a video first.")
            return

        output_path = QFileDialog.getSaveFileName(self, "Save Video", "", "MP4 Files (*.mp4)")[0]
        if not output_path:
            return

        # OpenCV video processing
        video = cv2.VideoCapture(self.video_path)
        frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = video.get(cv2.CAP_PROP_FPS)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

        while True:
            ret, frame = video.read()
            if not ret:
                break

            cc_value = self.cc_slider.value() / 100
            brightness = self.brightness_slider.value() / 100.0
            contrast = self.contrast_slider.value() / 100.0
            hue_value = self.hue_slider.value()
            sharpness = self.sharpness_slider.value() / 100.0
            saturation = self.saturation_slider.value() / 100.0
            rotate_angle = self.rotate_slider.value()

            frame = self.apply_color_correction(frame, cc_value)
            frame = cv2.convertScaleAbs(frame, alpha=1 + contrast, beta=brightness * 255)
            frame = self.apply_hue(frame, hue_value)
            frame = self.apply_sharpness(frame, sharpness)
            frame = self.apply_saturation(frame, saturation)
            frame = self.apply_rotation(frame, rotate_angle)

            out.write(frame)

        video.release()
        out.release()

        QMessageBox.information(self, "Success", "Video has been exported successfully!")

    def show_creator_popup(self):
        """ Show a popup to credit the creator """
        QMessageBox.information(self, "Creator", "This tool was made by https://t.me/hqqwwside")

if __name__ == "__main__":
    app = QApplication([])
    window = TikTokVideoTool()
    window.show()
    app.exec_()
