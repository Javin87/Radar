# MicroPython Radar System with Web Interface

This project implements a real-time radar system using MicroPython and an ESP32 board. It scans the surroundings with an ultrasonic sensor mounted on a servo motor and serves a live radar visualization through a built-in web server over Wi-Fi. This project does **not** use an OLED display or buzzer.

## 🌐 Features

- **Radar Scanning** with a rotating HC-SR04 ultrasonic sensor
- **Real-Time Web Interface** served from the ESP32
- **Auto-Trigger Mechanism** (e.g., for activating a servo-based gun)
- **Wi-Fi Access Point Mode** for local connectivity without router
- Clean radar-style visualization directly in a browser

## 🧰 Hardware Used

- ESP32 development board
- HC-SR04 Ultrasonic Distance Sensor
- SG90 Servo Motor (for scanning)
- Gun Servo Motor (for simulated "firing")
- Jumper Wires & Breadboard or PCB

> No OLED display and no buzzer are used in this project.

## 🔌 Pin Configuration

| Component      | ESP32 GPIO |
|----------------|------------|
| HC-SR04 Trigger| 4          |
| HC-SR04 Echo   | 5          |
| Radar Servo    | 27         |
| Gun Servo      | 25         |

** I have used 3 Servos as gun. you can modify it how you need. **

(You may adjust these pins in the script as needed.)

## 📁 Project Files

Make sure the following files are uploaded to the ESP32:

- `Radar_Source.py` – main MicroPython script
- `hc_sr04.py` – helper module for interfacing with the HC-SR04 sensor

> These files can be uploaded using tools like [Thonny](https://thonny.org/), uPyCraft, or `ampy`.

## ⚙️ How It Works

1. The ESP32 runs in **Access Point mode** and hosts a web server.
2. The radar servo sweeps between defined angles.
3. The HC-SR04 sensor measures distance at each step.
4. Detected objects are displayed in real-time on the web interface.
5. If an object is detected within a set threshold (e.g., under 20 cm), the gun servo is triggered automatically.

## 📲 How to Use

1. Upload the required files to your ESP32.
2. Power the board.
3. Connect your phone or computer to the ESP32’s Wi-Fi (e.g., `RadarSystem` with password `12345678`).
4. Open your browser and visit `http://192.168.4.1` to see the live radar interface.

## 💡 Future Improvements (Optional Ideas)

- Add support for Wi-Fi **Station mode** (connect to existing router)
- Export detection logs or activity to a file
- Add configuration panel on web UI (e.g., angle limits, firing range)
- Optional: integrate camera module for real-time imaging


## 📃 License

This project is developed and maintained by [Taha Samadi]. All rights reserved. No part of this code may be used, modified, or distributed without explicit permission from the author.

---

Made with passion using MicroPython 🐍⚙️
