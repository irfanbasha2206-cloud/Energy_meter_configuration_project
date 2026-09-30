# ⚡ Smart Energy & Climate Monitoring System

An IoT-based real-time electrical energy and environmental monitoring system built with **Raspberry Pi 3**. The system measures AC current drawn by electrical loads (e.g., lamps) via a current transformer, performs high-precision analog-to-digital conversion using the **ADS1115**, computes instantaneous power and cumulative energy consumption (Watt-hours & kWh units), tracks environmental climate factors with a **DHT11** sensor, displays a live formatted terminal dashboard, and logs all telemetry to a local **SQLite** database.

---

## 📌 Features

- **Analog-to-Digital Conversion (ADC):** Reads continuous analog voltage from the CT1270 current sensor using the 16-bit ADS1115 module over I2C (`0x48`).
- **Real-Time Electrical Calculations:**
  - Calculates true load current (Amperes) using calibrated sensor division.
  - Computes active power in Watts ($P = V \times I$ at 220V AC).
  - Integrates power over time to determine accumulated energy in **Watt-hours (Wh)** and commercial **Units (kWh)**.
- **Environmental Tracking:** Collects live ambient temperature (°C) and calibrated relative humidity (%) using the DHT11 sensor.
- **Clean CLI Dashboard:** Uses fixed-width ASCII formatting and ANSI screen clearing for an organized, non-scrolling, live-refreshing terminal table.
- **Persistent Local Database:** Automatically records timestamped metrics into SQLite (`sensor_data.db`) with disk commits to ensure data survives reboots and shutdowns.

---

## 🛠️ Hardware Requirements

| Component | Model / Specification | Purpose |
| :--- | :--- | :--- |
| **SBC** | Raspberry Pi 3 Model B / B+ | Central controller & data logger |
| **ADC Module** | ADS1115 (16-bit, 4-Channel) | Converts CT analog voltage to digital |
| **Current Sensor** | CT1270 Current Transformer | Non-invasive AC line current sensing |
| **Climate Sensor** | DHT11 | Ambient temperature & humidity monitoring |
| **Electrical Load** | AC 230V / 220V Lamp | Test load for energy measurement |
| **Accessories** | Jumper wires, Breadboard, 5V 3A Power Supply | Wiring & hardware interfacing |

---

## 🔌 Pinout & Wiring Diagram

### 1. Raspberry Pi 3 ↔ ADS1115 (I2C)
| ADS1115 Pin | Raspberry Pi Pin | Description |
| :--- | :--- | :--- |
| **VDD** | Pin 1 | 3.3V Power |
| **GND** | Pin 9 | Ground |
| **SCL** | Pin 5 | GPIO 3 (I2C SCL) |
| **SDA** | Pin 3 | GPIO 2 (I2C SDA) |
| **ADDR** | Pin 9 / ADS1115 GND | Sets I2C Address to `0x48` |

### 2. CT1270 Sensor ↔ ADS1115
| CT1270 Pin | Connection Target | Description |
| :--- | :--- | :--- |
| **VCC** | Raspberry Pi Pin 1 (3.3V) | Module supply |
| **GND** | Raspberry Pi GND | Ground reference |
| **OUT / Signal** | ADS1115 **A0** | Analog voltage output |
| **CT Core (Clamp)** | AC Phase (Live) Wire Only | Induction sensing of load current |

> ⚠️ **Safety Warning:** Ensure the CT clamp is wrapped strictly around the **Phase (Live)** wire, never around both Live and Neutral simultaneously. Disconnect AC mains when altering connections.

### 3. DHT11 ↔ Raspberry Pi 3
| DHT11 Pin | Raspberry Pi Pin | Description |
| :--- | :--- | :--- |
| **VCC (+)** | Pin 2 or Pin 4 | 5V / 3.3V Power |
| **DATA (Out)** | Pin 7 | GPIO 4 |
| **GND (-)** | Pin 6 | Ground |

---

## ⚙️ Software Configuration & Prerequisites

### 1. Enable Hardware I2C on Raspberry Pi
```bash
sudo raspi-config
