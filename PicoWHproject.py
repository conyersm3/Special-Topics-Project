import time
import network
import socket
import ucryptolib
import random
from machine import Pin, PWM, I2C
from pico_i2c_lcd import I2cLcd

# Wi-Fi credentials
SSID = " " # Replace with your SSID
PASSWORD = " " # Replace with your WIFI password
PORT = 12345

# AES encryption key (128-bit)
AES_KEY = b"thisis128bitkey!"

# GPIO setup for buzzers (Pin 14 for Buzzer 1, Pin 15 for Buzzer 2)
BUZZER_PIN_1 = 14
BUZZER_PIN_2 = 15
buzzer1 = PWM(Pin(BUZZER_PIN_1, Pin.OUT))
buzzer2 = PWM(Pin(BUZZER_PIN_2, Pin.OUT))

# I2C setup for LCD 1602 (SCL: GPIO 5, SDA: GPIO 4)
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
LCD_ADDR = 0x27
lcd = I2cLcd(i2c, LCD_ADDR, 2, 16)

# Note frequencies (in Hz)
note_freqs = {
    "REST": 0,
    "NOTE_C4": 262,
    "NOTE_D4": 294,
    "NOTE_E4": 330,
    "NOTE_F4": 349,
    "NOTE_G4": 392,
    "NOTE_A4": 440,
    "NOTE_B4": 494,
    "NOTE_C5": 523,
    "NOTE_D5": 587,
    "NOTE_E5": 659,
    "NOTE_F5": 698,
    "NOTE_G5": 784,
    "NOTE_A5": 880,
}

# Song of Storms notes and durations (in quarter notes)
song_of_storms = [
    ("NOTE_D4", 0.25), ("NOTE_A4", 0.25), ("NOTE_A4", 0.25), ("REST", 0.125),
    ("NOTE_E4", 0.125), ("NOTE_B4", 0.5), ("NOTE_F4", 0.25), ("NOTE_C5", 0.25),
    ("NOTE_C5", 0.25), ("REST", 0.125), ("NOTE_E4", 0.125), ("NOTE_B4", 0.5),
    ("NOTE_D4", 0.25), ("NOTE_A4", 0.25), ("NOTE_A4", 0.25), ("REST", 0.125),
    ("NOTE_E4", 0.125), ("NOTE_B4", 0.5), ("NOTE_F4", 0.25), ("NOTE_C5", 0.25),
    ("NOTE_C5", 0.25), ("REST", 0.125), ("NOTE_E4", 0.125), ("NOTE_B4", 0.5),
    ("NOTE_D4", 0.125), ("NOTE_F4", 0.125), ("NOTE_D5", 0.5),
    ("NOTE_D4", 0.125), ("NOTE_F4", 0.125), ("NOTE_D5", 0.5),
    ("NOTE_E5", 0.375), ("NOTE_F5", 0.125), ("NOTE_E5", 0.125), ("NOTE_E5", 0.125),
    ("NOTE_E5", 0.125), ("NOTE_C5", 0.125), ("NOTE_A4", 0.5), ("NOTE_A4", 0.25),
    ("NOTE_D4", 0.25), ("NOTE_F4", 0.125), ("NOTE_G4", 0.125), ("NOTE_A4", 0.75),
    ("NOTE_A4", 0.25), ("NOTE_D4", 0.25), ("NOTE_F4", 0.125), ("NOTE_G4", 0.125),
    ("NOTE_E4", 0.75), ("NOTE_D4", 0.125), ("NOTE_F4", 0.125), ("NOTE_D5", 0.5),
    ("NOTE_D4", 0.125), ("NOTE_F4", 0.125), ("NOTE_D5", 0.5),
    ("NOTE_E5", 0.375), ("NOTE_F5", 0.125), ("NOTE_E5", 0.125), ("NOTE_E5", 0.125),
    ("NOTE_E5", 0.125), ("NOTE_C5", 0.125), ("NOTE_A4", 0.5), ("NOTE_A4", 0.25),
    ("NOTE_D4", 0.25), ("NOTE_F4", 0.125), ("NOTE_G4", 0.125), ("NOTE_A4", 0.5),
    ("NOTE_A4", 0.25), ("NOTE_D4", 1.0)
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

# Function to play a note on both buzzers
def play_note(note, duration):
    frequency = note_freqs.get(note, 0)
    if frequency > 0:
        buzzer1.duty_u16(30000)
        buzzer1.freq(frequency)
        buzzer2.duty_u16(30000)
        buzzer2.freq(frequency)
    else:
        buzzer1.duty_u16(0)
        buzzer2.duty_u16(0)
    time.sleep(duration)
    buzzer1.duty_u16(0)
    buzzer2.duty_u16(0)
    time.sleep(0.01)  # Short pause between notes

# Function to play the Song of Storms
def play_song():
    print("Playing Song of Storms...")
    for note, duration in song_of_storms:
        play_note(note, duration)

# Main function
def main():
    connect_to_wifi()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", PORT))
    sock.listen(1)
    print(f"Receiver is listening on port {PORT}...")

    while True:
        try:
            print("Waiting for a connection...")
            conn, addr = sock.accept()
            print(f"Connection established with {addr}")

            # Receive encrypted data and send a PIN
            data = conn.recv(1024)
            print("Received encrypted message.")

            # Generate and send the PIN
            pin = "{:04d}".format(random.randint(0, 9999))
            lcd.clear()
            lcd.putstr(f"PIN: {pin}")
            conn.send(pin.encode())
            print(f"Sent PIN: {pin}")

            # Wait for Good-to-Go signal
            response = conn.recv(1024).decode()
            if response == "Good-to-Go":
                lcd.clear()
                lcd.putstr("Access Granted")
                print("Access Granted")

                # Display GPS coordinates
                time.sleep(2)
                lat = round(random.uniform(-90, 90), 6)
                lon = round(random.uniform(-180, 180), 6)
                lcd.clear()
                lcd.putstr(f"Lat:{lat}")
                lcd.move_to(0, 1)
                lcd.putstr(f"Lon:{lon}")

                # Play the song
                play_song()
            else:
                lcd.clear()
                lcd.putstr("Access Denied")
                print("Access Denied")

            conn.close()

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()

