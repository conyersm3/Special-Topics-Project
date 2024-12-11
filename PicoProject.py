# Combined Code for Transmitter Pico W (transmitter side)

import time
import network
import socket
import ucryptolib
import random
from machine import Pin, PWM, I2C
from mfrc522 import SimpleMFRC522

# Wi-Fi credentials
SSID = "MyOptimum ba9973"
PASSWORD = "brick-762-400"  # Replace with your actual Wi-Fi password
RECEIVER_IP = "192.168.1.193"  # Replace with the actual receiver IP
PORT = 12345

# AES encryption key (128-bit)
AES_KEY = b"thisis128bitkey!"

# GPIO setup for RGB LED
led_red = Pin(15, Pin.OUT)
led_green = Pin(16, Pin.OUT)
led_blue = Pin(17, Pin.OUT)

# Initialize the SimpleMFRC522 reader with custom pins
rfid_reader = SimpleMFRC522(sck=2, mosi=3, miso=4, cs=1, rst=0)

# Keypad configuration
row_pins = [Pin(12, Pin.OUT), Pin(11, Pin.OUT), Pin(10, Pin.OUT), Pin(9, Pin.OUT)]
col_pins = [Pin(8, Pin.IN, Pin.PULL_DOWN), Pin(7, Pin.IN, Pin.PULL_DOWN), Pin(6, Pin.IN, Pin.PULL_DOWN), Pin(5, Pin.IN, Pin.PULL_DOWN)]
keys = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

# Function to connect to Wi-Fi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Connecting to Wi-Fi...")
    while not wlan.isconnected():
        time.sleep(1)
    print("Connected to Wi-Fi!")
    print("IP Address:", wlan.ifconfig()[0])

# Function to set RGB LED color
def set_rgb_color(red, green, blue):
    led_red.value(red)
    led_green.value(green)
    led_blue.value(blue)

# Function to pad messages to be multiples of 16 bytes
def pad_message(message):
    message_bytes = message.encode('utf-8')
    padding_length = 16 - (len(message_bytes) % 16)
    return message_bytes + b" " * padding_length

# Function to encrypt a message
def encrypt_message(message):
    padded_message = pad_message(message)
    cipher = ucryptolib.aes(AES_KEY, 1)  # 1 represents ECB mode
    encrypted = cipher.encrypt(padded_message)
    return encrypted

# Function to get user input from the keypad
def get_pin_from_keypad():
    pin = ""
    print("Enter the 4-digit PIN followed by #: ")
    while True:
        for row_index, row in enumerate(row_pins):
            row.on()
            for col_index, col in enumerate(col_pins):
                if col.value():
                    key = keys[row_index][col_index]
                    print(f"Key pressed: {key}")
                    if key == "#":
                        row.off()
                        return pin
                    elif key.isdigit() and len(pin) < 4:
                        pin += key
                        print(f"Current PIN: {pin}")
                    time.sleep(0.3)  # Debounce delay
            row.off()

# Main function
def main():
    connect_to_wifi()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        sock.connect((RECEIVER_IP, PORT))
        set_rgb_color(0, 0, 1)  # Blue LED for waiting on RFID
        print("Place RFID card near the reader...")
        
        while True:
            try:
                id, text = rfid_reader.read()
                print(f"RFID ID: {id}, Text: {text}")
                set_rgb_color(0, 1, 0)  # Green LED for verified RFID

                # Encrypt and send a message
                message = f"RFID_OK: {id}"
                encrypted_msg = encrypt_message(message)
                sock.send(encrypted_msg)
                print("Sent encrypted message to receiver")
                
                # Receive the PIN from the receiver
                pin = sock.recv(1024).decode()
                print(f"Received PIN: {pin}")
                
                # Prompt user to enter the PIN on the keypad
                entered_pin = get_pin_from_keypad()
                print(f"Entered PIN: {entered_pin}")
                
                if entered_pin == pin:
                    print("PIN is correct!")
                    sock.send("Good-to-Go".encode())
                else:
                    print("Incorrect PIN!")
                    sock.send("Access Denied".encode())
                
                time.sleep(5)

            except Exception as e:
                print(f"Error reading RFID: {e}")
                set_rgb_color(1, 0, 0)  # Red LED for error
                time.sleep(5)
    
    except Exception as e:
        print(f"Connection error: {e}")
    
    finally:
        sock.close()
        print("Socket closed")

if __name__ == "__main__":
    main()

