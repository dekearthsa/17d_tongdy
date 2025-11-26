from queue import Queue, Empty
# from mock_sensor_poller import create_mock_poller 
from sensor_poller import SensorPoller
import time
import sqlite3

## for mocking ##
import threading
from typing import Any
import random
##

PATH_DB = "/Users/pcsishun/project_envalic/17d_control/17d_backend/hlr_db.db"

### for mocking  ###
def create_mock_poller(ui_queue: Queue, polling_interval: float = 5.0):
    """
    สร้าง mock poller ที่มี .start() / .stop() เหมือน SensorPoller
    แต่จะยิง mock data ใส่ ui_queue เป็นระยะ ๆ

    - sensor_type "tongdy" → ใช้กับ save_to_db_tongdy
    - sensor_type "interlock" → ใช้กับ save_to_db_interlock
    """

    class MockPoller:
        def __init__(self, queue: Queue, interval: float):
            self.queue = queue
            self.interval = interval
            self._stop_event = threading.Event()
            self._thread: threading.Thread | None = None

        def start(self):
            # กันเรียก start ซ้ำ
            if self._thread and self._thread.is_alive():
                return
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

        def stop(self):
            self._stop_event.set()
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=2)

        def _run(self):
            while not self._stop_event.is_set():
                now_ms = int(time.time() * 1000)

                # ── mock tongdy 2 ตัว: before_exhaust / after_exhausts
                for sid in ("before_exhaust", "after_exhausts"):
                    self.queue.put({
                        "sensor_type": "tongdy",
                        "sensor_id": sid,
                        "payload": {
                            "temperature": round(24 + random.uniform(-1.5, 1.5), 2),
                            "humid": round(55 + random.uniform(-8, 8), 2),
                            "co2": round(600 + random.uniform(-80, 80), 2),
                        },
                        "timestamp": now_ms,
                    })

                # ── mock interlock_4c 1 ตัว
                mode = random.randint(0, 5)  # 0..5
                temp_before_filter = round(30 + random.uniform(-2, 2), 2)
                fan_speed = random.randint(0, 100)
                voc = round(200 + random.uniform(-50, 50), 2)

                self.queue.put({
                    "sensor_type": "interlock",
                    "sensor_id": "interlock_4c",
                    "payload": {
                        "temperature": round(30 + random.uniform(-2, 2), 2),
                        "humid": round(50 + random.uniform(-10, 10), 2),
                        "co2": round(800 + random.uniform(-100, 100), 2),
                        "operation_mode": mode,
                        "temp_before_filter": temp_before_filter,
                        "fan_speed": fan_speed,
                        "voc": voc,
                    },
                    "timestamp": now_ms,
                })

                # จะยิงชุดใหม่ทุก polling_interval วินาที
                time.sleep(self.interval)

    return MockPoller(ui_queue, polling_interval)

####

def open_conn():
    conn = sqlite3.connect(PATH_DB, check_same_thread=False, timeout=5)
    conn.row_factory = sqlite3.Row
    try:
        # ใช้ WAL + กำหนด busy_timeout ลดโอกาส locked
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")
    except Exception:
        pass
    return conn

# ─────────────────────────────────────────────────────────────
# Save tongdy data
# ─────────────────────────────────────────────────────────────
def save_to_db_tongdy(sensor_id,sensor_type, timestamp, temp, humid, co2):
    try:
        conn = open_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sensor_data_exhaust (timestamp, sensor_type,sensor_id,co2,temp,humid )
            VALUES (?, ?, ?,?, ?, ?)
        """, (timestamp,sensor_type, sensor_id, co2, temp, humid ))
        conn.commit()
    except Exception as err:
        print(f"error when save in database {err}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

# ─────────────────────────────────────────────────────────────
# Save interlock data
# ─────────────────────────────────────────────────────────────
def save_to_db_interlock(sensor_id, sensor_type,timestamp, temp, humid, co2, operation_mode, temp_before_filter, fan_speed, voc):
    try:
        conn = open_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sensor_data_interlock (timestamp,sensor_type, sensor_id, temp, humid, co2, operation_mode, temp_before_filter, fan_speed, voc )
            VALUES (?, ?, ?,?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, sensor_type,sensor_id, temp, humid, co2, operation_mode, temp_before_filter, fan_speed, voc ))
        conn.commit()
    except Exception as err:
        print(f"error when save in database {err}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

# ─────────────────────────────────────────────────────────────
# Save meter power data
# ─────────────────────────────────────────────────────────────

def save_to_db_meter():
    ## เตรียม function ไว้ก่อนยังไม่ได้ใช้งาน 
    pass

# ─────────────────────────────────────────────────────────────
# Main loop (drain queue แบบไม่พึ่ง .empty())
# ─────────────────────────────────────────────────────────────
def main():
    set_queue = Queue()
    poller = SensorPoller(ui_queue=set_queue, polling_interval=10)
    # poller = create_mock_poller(ui_queue=set_queue, polling_interval=10)
    # เริ่มอ่าน 10 วินาที แล้วหยุด จากนั้นดูดคิวให้หมด
    poller.start()
    time.sleep(10)
    poller.stop()

    while True:
        try:
            data_sensor = set_queue.get_nowait()  # แทนการเช็ค empty()
            # print("data_sensor => ",data_sensor)
        except Empty:
            break
        now_ms = int(time.time() * 1000)

        if data_sensor['sensor_type'] == "tongdy":
            save_to_db_tongdy(
                sensor_id=data_sensor['sensor_id'],
                sensor_type=data_sensor['sensor_type'],
                timestamp=now_ms,
                temp=data_sensor['payload']['temperature'],
                humid=data_sensor['payload']['humid'],
                co2=data_sensor['payload']['co2'],
                )
        elif data_sensor['sensor_type'] == "interlock":
            save_to_db_interlock(
                sensor_id=data_sensor['sensor_id'],
                sensor_type=data_sensor['sensor_type'],
                timestamp=now_ms,
                temp=data_sensor['payload']['temperature'],
                humid=data_sensor['payload']['humid'],
                co2=data_sensor['payload']['co2'],
                operation_mode=data_sensor['payload']['operation_mode'],
                temp_before_filter=data_sensor['payload']['temp_before_filter'],
                fan_speed=data_sensor['payload']['fan_speed'],
                voc=data_sensor['payload']['voc'],
            )
        elif data_sensor['sensor_type'] == "meter":
            print("under development.")
            pass
        else:
            print(f"No sensor type match: {data_sensor['sensor_id']}")
            pass
    time.sleep(5)

# ─────────────────────────────────────────────────────────────
# Entrypoint
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Service poller started")
    try:
        while True:
            main()
    except KeyboardInterrupt:
        pass

