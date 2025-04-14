# This project implements a radar system using MicroPython and an ESP32 By Taha Samadi.
# Make sure to check the README.md file for detailed setup and usage instructions.

import network
import usocket as socket
import gc
from machine import Pin, PWM, Timer
import time
from _thread import start_new_thread
import json
from hc_sr04 import HCSR04
import math
# Initialize the ultrasonic sensor
sensor = HCSR04(trigger_pin=4, echo_pin=5)

# Servo motor settings
pwm1 = PWM(Pin(27), freq=50, duty=0)  # Servo 1
pwm2 = PWM(Pin(26), freq=50, duty=0)  # Servo 2
pwm3 = PWM(Pin(25), freq=50, duty=0)  # Servo 3
pwm4 = PWM(Pin(33), freq=50, duty=0)  # Servo 4

def Servo1(angle):
    pwm1.duty(int(((angle) / 180 * 2 + 0.5) / 20 * 1023))    # The servo that ultrasonic mounted on it

def Servo2(angle):
    pwm2.duty(int(((angle) / 180 * 2 + 0.5) / 20 * 1023))

def Servo3(angle):
    pwm3.duty(int(((angle) / 180 * 2 + 0.5) / 20 * 1023))

def Servo4(angle):
    pwm4.duty(int(((angle) / 180 * 2 + 0.5) / 20 * 1023))
# Refrence Of Servos
Servo3(0)
Servo2(0)
Servo4(0)

# Access Point settings
essid = 'YOUR_AP'
password = 'PASSWORD'

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=essid, password=password)

print('Access Point Mode')
print(ap.ifconfig())
# Servo motor angle
angle = 0
obstacles = {i: None for i in range(0, 181, 10)}  # Dictionary to store obstacle information for each angle

# Function to generate the HTML webpage
def web_page():
    html = """<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RADAR</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #000;
        }

        .radar {
            position: relative;
            width: 1000px;
            height: 500px;
            border-top-left-radius: 500px;
            border-top-right-radius: 500px;
            background: rgba(0, 255, 0, 0.1);
            border-top: 4px solid rgba(0, 255, 0, 0.5);
            overflow: hidden;
        }

        .line {
            position: absolute; 
            width: 4px;
            height: 500px;
            background: rgba(0, 255, 0, 0.8);
            bottom: 0;
            left: 50%;
            transform-origin: bottom center;
            transform: translateX(-50%) rotate(90deg);
        }

        .degree {
            position: absolute;
            color: rgba(0, 255, 0, 0.8);
            font-size: 18px;
            transform: translate(-50%, -50%);
        }

        .dot {
            position: absolute;
            width: 10px;
            height: 10px;
            background: red;
            border-radius: 50%;
        }

        .distance-label {
            position: absolute;
            color: red;
            font-size: 12px;
            transform: translate(-50%, -50%);
        }
    </style>
</head>
<body>
    <div class="radar" id="radar">
        <div class="line" id="radarLine"></div>
    </div>

    <script>
        const radar = document.getElementById('radar');

        function drawDot(angle, distance) {
            const dot = document.createElement('div');
            dot.className = 'dot';
            const distanceLabel = document.createElement('div');
            distanceLabel.className = 'distance-label';
            distanceLabel.textContent = distance.toFixed(2) + ' cm';

            const angleRad = angle * Math.PI / 180;
            const distanceRatio = distance / 300; // 300 cm is the max range
            const x = 500 + 480 * Math.cos(angleRad) * distanceRatio;
            const y = 500 - 480 * Math.sin(angleRad) * distanceRatio;

            dot.style.left = `${x}px`;
            dot.style.top = `${y}px`;

            distanceLabel.style.left = `${x}px`;
            distanceLabel.style.top = `${y - 15}px`;

            radar.appendChild(dot);
            radar.appendChild(distanceLabel);
        }

        function updateRadar(angle, obstacles) {
            const radarLine = document.getElementById('radarLine');
            radarLine.style.transform = 'translateX(-50%) rotate(' + (90 - angle) + 'deg)';

            // Remove old dots
            document.querySelectorAll('.dot, .distance-label').forEach(el => el.remove());

            // Draw new dots
            obstacles.forEach(obs => {
                if (obs !== null) {
                    drawDot(obs.angle, obs.distance);
                }
            });
        }

        // Fetch current servo angle and obstacle status periodically
        function fetchAngle() {
            fetch('/angle')
                .then(response => response.json())
                .then(data => {
                    const angle = data.angle;
                    const obstacles = Object.entries(data.obstacles)
                        .map(([angle, distance]) => distance ? { angle: parseInt(angle), distance: distance.distance } : null)
                        .filter(obs => obs !== null);

                    updateRadar(angle, obstacles);
                })
                .catch(error => console.error('Error fetching angle:', error));
        }

        // Add degree markers
        for (let i = 0; i <= 180; i += 10) {
            const degree = document.createElement('div');
            degree.className = 'degree';
            const angle = (i * Math.PI) / 180;
            const x = 500 + 480 * Math.cos(angle);
            const y = 500 - 480 * Math.sin(angle);
            degree.style.left =`${x}px`
            degree.style.top = `${y}px`
            degree.textContent = i;
            radar.appendChild(degree);
        }

        // Start fetching the angle every 500ms
        setInterval(fetchAngle, 500);
    </script>
</body>
</html>"""
    return html

# Web server function
def start_web_server():
    s = socket.socket()
    s.bind(('', 80))
    s.listen(5)

    while True:
        try:
            if gc.mem_free() < 102000:
                gc.collect()

            conn, addr = s.accept()
            conn.settimeout(3.0)
            print('Got a connection from %s' % str(addr))
            request = conn.recv(1024)
            request = str(request)

            # Check if request is for the angle
            if '/angle' in request:
                response = json.dumps({'angle': angle, 'obstacles': obstacles})
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: application/json\n')
                conn.send('Connection: close\n\n')
                conn.sendall(response)
            else:
                # Send the webpage with the current servo angle
                response = web_page()
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/html\n')
                conn.send('Connection: close\n\n')
                conn.sendall(response)

            conn.close()

        except OSError as e:
            conn.close()
            print('Connection closed')

# Servo rotation function and update angle
def rotate_servo():
    global angle, obstacles
    while True:
        # Increase the angle (0 to 180)
        while angle < 180:
            angle += 10
            Servo1(angle)
            time.sleep(0.3)
            # Check distance
            distance = sensor.distance_cm()
            print(distance)
            if distance > 0 and distance <= 300:    # This is changable, change to the distance you need.
                # Update obstacles list
                obstacles[angle] = {'distance': distance}

                if distance < 50 and distance > 0:   # You can increase the range of sensor on your own(in my case it is 50 cm)
                    # Calculate the angle for servo 26
                    a = math.atan(distance / 7.5) * 180 / math.pi
                    Servo2(a)  # Set servo 26 to calculated angle

                    # Set servo 33 to the angle as same as sensor's servo' angle
                    Servo4(angle)
                        
                    # Move servo 25 to 65 degrees, wait 1 seconds, then return to 0 degrees
                    Servo3(65)
                    time.sleep(1)
                    Servo3(0)
                       
                if distance > 50:
                    pass
            else:
                # Remove obstacle if no longer detected
                obstacles[angle] = None
        # Decrease the angle (return from 180 to 0)
        while angle > 0:
            angle -= 10
            Servo1(angle)
            time.sleep(0.3)
            # Check distance again for the return path
            distance = sensor.distance_cm()
            print(distance)
            if distance > 0 and distance <= 300:
                # Update obstacles list
                obstacles[angle] = {'distance': distance}

                if distance < 50 and distance > 0:   # You can increase the range of sensor on your own(in my case it is 50 cm)
                        
                        # Calculate the angle for servo 26
                        a = math.atan(distance / 7.5) * 180 / math.pi
                        Servo2(a)  # Set servo 26 to calculated angle
                        # Set servo 33 to the angle as same as sensor's servo' angle
                        Servo4(angle)
                        
                        # Move servo 25 to 65 degrees, wait 1 seconds, then return to 0 degrees
                        Servo3(65)
                        time.sleep(1)
                        Servo3(0)
                       
                if distance > 50:
                    pass
            else:
                # Remove obstacle if no longer detected
                obstacles[angle] = None


# Run the web server and servo motor rotation
start_new_thread(start_web_server, ())
rotate_servo()