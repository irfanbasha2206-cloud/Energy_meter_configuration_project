import sqlite3
import time
from datetime import datetime
import board
import busio
import adafruit_dht
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

conn = sqlite3.connect("/home/pi/Desktop/Smart_Energy_Meter/sensor_data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS energy_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    voltage REAL,
    current REAL,
    power REAL,
    total_wh REAL,
    units_kwh REAL,
    temperature REAL,
    humidity REAL
)
""")
conn.commit()

dht_device = adafruit_dht.DHT11(board.D4, use_pulseio=False)
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)
chan_ct = AnalogIn(ads, 0)

AC_VOLTAGE = 220.0
DIVIDER_FACTOR = 1.37

total_wh = 0.0
last_dht_time = 0
temperature = 0.0
humidity = 70.0
last_time = time.time()

try:
    while True:
        now_time = time.time()
        elapsed_seconds = now_time - last_time
        last_time = now_time

        raw_adc = chan_ct.value
        voltage = chan_ct.voltage
        current_amps = voltage / DIVIDER_FACTOR
        power_watts = AC_VOLTAGE * current_amps

        instant_wh = (power_watts * elapsed_seconds) / 3600.0
        total_wh += instant_wh
        units_kwh = total_wh / 1000.0

        if now_time - last_dht_time >= 2.0:
            last_dht_time = now_time
            try:
                t = dht_device.temperature
                h = dht_device.humidity
                if t is not None and h is not None:
                    temperature = float(t)
                    humidity = float(h) + 7.0
            except RuntimeError:
                pass

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO energy_logs (timestamp, voltage, current, power, total_wh, units_kwh, temperature, humidity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (now_str, round(voltage, 3), round(current_amps, 3), round(power_watts, 2), 
              round(total_wh, 4), round(units_kwh, 6), temperature, humidity))
        conn.commit()

        val_ac_v     = f"{AC_VOLTAGE:.1f} V"
        val_ct_v     = f"{voltage:.3f} V"
        val_current  = f"{current_amps:.3f} A"
        val_power    = f"{power_watts:.2f} W"
        val_wh       = f"{total_wh:.4f} Wh"
        val_kwh      = f"{units_kwh:.6f} kWh"
        val_temp     = f"{temperature:5.1f} C"
        val_humidity = f"{humidity:5.1f} %"

        print("\033[H\033[J", end="")
        print("+------------------------------------------------------+")
        print("|           REAL-TIME ENERGY & CLIMATE MONITOR         |")
        print("+------------------------------------------------------+")
        print(f"| Timestamp  : {now_str:<39} |")
        print("+------------------------------+-----------------------+")
        print("| Parameter                    | Value                 |")
        print("+------------------------------+-----------------------+")
        print(f"| AC Line Voltage              | {val_ac_v:>21} |")
        print(f"| CT Pin Voltage (A0)          | {val_ct_v:>21} |")
        print(f"| Load Current                 | {val_current:>21} |")
        print(f"| Active Power                 | {val_power:>21} |")
        print(f"| Accumulated Energy           | {val_wh:>21} |")
        print(f"| Total Energy Units           | {val_kwh:>21} |")
        print("+------------------------------+-----------------------+")
        print(f"| Temperature                  | {val_temp:>21} |")
        print(f"| Humidity                     | {val_humidity:>21} |")
        print("+------------------------------+-----------------------+")
        print("| Status: RUNNING | SQLite: OK | Exit: Ctrl + C        |")
        print("+------------------------------------------------------+")

        time.sleep(1.0)

except KeyboardInterrupt:
    conn.close()
    dht_device.exit()
    print("\n\nStopped cleanly. Database closed.")