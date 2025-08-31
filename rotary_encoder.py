# code.py (CircuitPython on QT Py ESP32-S2)
import time, json
import board, busio, usb_cdc
from adafruit_seesaw.seesaw import Seesaw
from adafruit_seesaw import rotaryio, digitalio

i2c = busio.I2C(board.SCL, board.SDA)
ss = Seesaw(i2c, addr=0x36)

enc = rotaryio.IncrementalEncoder(ss)
btn = digitalio.DigitalIO(ss, 24)
btn.switch_to_input(pull=digitalio.Pull.UP)

ser = usb_cdc.data
last = enc.position

def emit(ev, **kw):
    msg = {"t": round(time.monotonic(), 3), "ev": ev, **kw}
    ser.write((json.dumps(msg) + "\n").encode("utf-8"))

emit("boot", raw=last, detents=last // 4)

while True:
    pos = enc.position
    if pos != last:
        emit("turn", raw=pos, delta=pos - last, detents=pos // 4)
        last = pos

    if not btn.value:
        emit("press")
        while not btn.value:
            time.sleep(0.01)
        emit("release")

    time.sleep(0.005)
