# IoT Temperature Monitor

Bidirectional serial communication between a PC server and a Raspberry Pi Pico W. The Pico reads temperature data and controls an RGB LED based on commands from the server.

---

## Requirements

- Python 3.13.0 with `pyserial` installed:
  ```
  pip install -r requirements.txt
  ```
- Raspberry Pi Pico W with MicroPython firmware
- DHT22 temperature sensor
- Common cathode RGB LED

---

## Running the Server

1. Connect the Raspberry Pi Pico W via USB.
2. Run the server script on the PC:
   ```
   python main_server.py
   ```
3. The server automatically detects the Pico by its USB Vendor ID — no manual port configuration needed.

---

## Uploading the Pico Script

1. Open `main_rpi.py` in [Thonny](https://thonny.org/).
2. Set the interpreter to **MicroPython (Raspberry Pi Pico)**.
3. Save the file to the Pico as `main.py` — it will then run automatically on boot.

---

## Wiring

| Component        | Pico GPIO |
|-----------------|-----------|
| DHT22 data       | GP20      |
| RGB LED — Red    | GP16      |
| RGB LED — Green  | GP17      |
| RGB LED — Blue   | GP18      |
| RGB LED — Common | GND       |

> **Note:** This project uses a **common cathode** RGB LED. Each channel must be connected through a 220–330 Ω resistor.

---

## Default Server Configuration

| Parameter              | Value  | Description                          |
|-----------------------|--------|--------------------------------------|
| `measure_period`       | 25000  | Measurement interval in ms           |
| `keep_alive_interval`  | 15     | Keep-alive send interval in seconds  |
| `BAUD`                 | 115200 | Serial baud rate                     |

---

## Temperature → LED Color Mapping

| Temperature   | Color  |
|--------------|--------|
| < 18 °C       | Blue   |
| 18 – 22 °C    | Cyan   |
| 22 – 25 °C    | Green  |
| 25 – 28 °C    | Yellow |
| > 28 °C       | Red    |
