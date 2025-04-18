import sys
import pyttsx3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QComboBox, QDial
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import speech_recognition as sr


class WashingMachineApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Smart Washing Machine")
        self.setGeometry(100, 100, 800, 600)

        # Initialize voice engine
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.mode_selected = None
        self.timer = None
        self.time_left = 0

        # Main Layout
        layout = QVBoxLayout()

        # Power Button
        self.power_button = QPushButton("Power On")
        self.power_button.clicked.connect(self.toggle_power)
        layout.addWidget(self.power_button)

        # Status Label
        self.status_label = QLabel("Machine is Off")
        self.status_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.status_label)

        # Mode Dial
        self.mode_dial = QDial()
        self.mode_dial.setMinimum(0)
        self.mode_dial.setMaximum(10)
        self.mode_dial.valueChanged.connect(self.update_mode)
        layout.addWidget(self.mode_dial)

        # Mode Label
        self.mode_label = QLabel("Select Mode")
        layout.addWidget(self.mode_label)

        # Time Label
        self.time_label = QLabel("Time Remaining: 0 min")
        layout.addWidget(self.time_label)

        # Temperature Slider
        temp_layout = QHBoxLayout()
        self.temp_label = QLabel("Temperature: 0°C")
        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setMinimum(0)
        self.temp_slider.setMaximum(100)
        self.temp_slider.valueChanged.connect(self.update_temperature)
        temp_layout.addWidget(self.temp_label)
        temp_layout.addWidget(self.temp_slider)
        layout.addLayout(temp_layout)

        # Spinner/Dryer Settings
        self.spinner_label = QLabel("Spinner/Dryer Settings")
        self.spinner_box = QComboBox()
        self.spinner_box.addItems(["No Heat", "Steam Dry", "Timed Dry"])
        layout.addWidget(self.spinner_label)
        layout.addWidget(self.spinner_box)

        # Start Wash Button
        self.start_wash_button = QPushButton("Start Wash")
        self.start_wash_button.clicked.connect(self.start_wash)
        layout.addWidget(self.start_wash_button)

        # Pause/Resume Button
        self.pause_button = QPushButton("Pause")
        self.pause_button.setEnabled(False)  # Disabled initially
        self.pause_button.clicked.connect(self.toggle_pause)
        layout.addWidget(self.pause_button)

        # Stop Wash Button
        self.stop_button = QPushButton("Stop Wash")
        self.stop_button.setEnabled(False)  # Disabled initially
        self.stop_button.clicked.connect(self.stop_wash_cycle)
        layout.addWidget(self.stop_button)

        # Activate Voice Command Button
        self.voice_command_button = QPushButton("Activate Voice Command")
        self.voice_command_button.clicked.connect(self.activate_voice_command)
        layout.addWidget(self.voice_command_button)


        self.setLayout(layout)

    def toggle_power(self):
        if self.power_button.text() == "Power On":
            self.power_button.setText("Power Off")
            self.status_label.setText("Machine is On")
            self.speak("Washing Machine is now powered on.")
        else:
            self.power_button.setText("Power On")
            self.status_label.setText("Machine is Off")
            self.speak("Washing Machine is now powered off.")

    def update_mode(self):
        modes = [
            "Cotton", "Synthetic", "Delicate", "Wool", "Quick Wash",
            "Heavy Duty", "Rinse and Spin", "Spin Only", "Eco", "Self-Clean", "Kid Cloth"
        ]
        self.mode_selected = modes[self.mode_dial.value()]
        self.mode_label.setText(f"Mode: {self.mode_selected}")
        time_required = [60, 45, 30, 40, 20, 80, 15, 10, 50, 90, 35]  # Predefined times
        self.time_left = time_required[self.mode_dial.value()]
        self.time_label.setText(f"Time Required: {self.time_left} min")
        self.speak(f"Mode set to {self.mode_selected}. Time required is {self.time_left} minutes.")

    def update_temperature(self):
        temperature = self.temp_slider.value()
        self.temp_label.setText(f"Temperature: {temperature}°C")
        self.speak(f"Temperature set to {temperature} degrees Celsius.")

    def start_wash(self):
        if not self.mode_selected:
            self.speak("Please select a mode before starting the wash.")
            return
        if self.power_button.text() == "Power On":
            self.speak("Please turn on the machine before starting the wash.")
            return

        self.speak(f"Starting {self.mode_selected} mode. Estimated time is {self.time_left} minutes.")
        self.status_label.setText(f"Running {self.mode_selected} mode.")
        self.start_timer()

    def start_timer(self):
        """Starts the wash cycle timer."""
        if self.timer:
            self.timer.stop()  # Stop any existing timer before starting a new one.

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.time_left_seconds = self.time_left * 60  # Convert minutes to seconds
        self.timer.start(1000)  # Update every second for real-time feedback

    def update_timer(self):
        """Updates the timer and displays remaining time."""
        if self.time_left_seconds > 0:
            self.time_left_seconds -= 1
            minutes = self.time_left_seconds // 60
            seconds = self.time_left_seconds % 60
            self.time_label.setText(f"Time Remaining: {minutes} min {seconds} sec")
        else:
            self.timer.stop()
            self.status_label.setText("Wash cycle completed.")
            self.speak("Wash cycle completed.")
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)

    def toggle_pause(self):
        """Pauses or resumes the timer."""
        if self.pause_button.text() == "Pause":
            self.timer.stop()
            self.pause_button.setText("Resume")
            self.status_label.setText("Wash cycle paused.")
            self.speak("Wash cycle paused.")
        else:
            self.timer.start(1000)  # Resume timer
            self.pause_button.setText("Pause")
            self.status_label.setText("Wash cycle resumed.")
            self.speak("Wash cycle resumed.")

    def stop_wash_cycle(self):
        """Stops the wash cycle and resets the timer."""
        if self.timer:
            self.timer.stop()
        self.time_left_seconds = 0
        self.time_label.setText("Time Remaining: 0 min 0 sec")
        self.status_label.setText("Wash cycle stopped.")
        self.speak("Wash cycle has been stopped.")
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)

    def activate_voice_command(self):
        self.speak("Voice command activated. Please say a command.")
        try:
            with sr.Microphone() as source:
                audio = self.recognizer.listen(source)
                command = self.recognizer.recognize_google(audio).lower()
                self.process_voice_command(command)
        except sr.UnknownValueError:
            self.speak("Sorry, I did not understand that.")
        except sr.RequestError:
            self.speak("Voice command system is currently unavailable.")

    def process_voice_command(self, command):
        # Handle voice commands
        if "turn on" in command or "power on" in command:
            self.toggle_power()
        elif "turn off" in command or "power off" in command:
            self.toggle_power()
        elif "start the wash" in command or "begin the wash cycle" in command:
            self.start_wash()
        elif "stop the timer" in command or "cancel the wash" in command:
            if self.timer:
                self.timer.stop()
                self.status_label.setText("Wash cycle stopped.")
                self.speak("Wash cycle stopped.")
        elif "pause the wash" in command:
            self.toggle_pause()
        elif "resume the wash" in command:
            self.toggle_pause()
        elif "set mode to" in command:
            mode = command.split("set mode to ")[1]
            modes = {
                "cotton": 0, "synthetic": 1, "delicate": 2, "wool": 3, "quick wash": 4,
                "heavy duty": 5, "rinse and spin": 6, "spin only": 7, "eco": 8,
                "self-clean": 9, "kid cloth": 10
            }
            if mode in modes:
                self.mode_dial.setValue(modes[mode])
        elif "set temperature to" in command or "adjust water temperature to" in command:
            temp = int(command.split("to ")[1].split()[0])
            self.temp_slider.setValue(temp)
        elif "set spinner to" in command or "choose" in command:
            spinner = command.split("to ")[1]
            if spinner in ["no heat", "steam dry", "timed dry"]:
                self.spinner_box.setCurrentText(spinner)

    def speak(self, message):
        self.engine.say(message)
        self.engine.runAndWait()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WashingMachineApp()
    window.show()
    sys.exit(app.exec())
