import time, json
import board, busio
import usb_cdc

from adafruit_seesaw.seesaw import Seesaw
from adafruit_seesaw import rotaryio, digitalio

i2c = busio.I2C(board.SCL, board.SDA)
ss = Seesaw(i2c, addr=0x36)

enc = rotaryio.IncrementalEncoder(ss)
btn = digitalio.DigitalIO(ss, 24)        # built-in push button on Adafruit board
btn.switch_to_input(pull=digitalio.Pull.UP)

last = enc.position
ser = usb_cdc.data    # shows up as /dev/ttyACM* on the Pi

def emit(ev, **kw):
    msg = {"t": time.monotonic(), "ev": ev, **kw}
    ser.write((json.dumps(msg) + "\n").encode("utf-8"))

emit("boot", pos=last)

while True:
    pos = enc.position
    if pos != last:
        # Many Seesaw encoders = 4 ticks per detent
        detents = pos // 4
        delta = pos - last
        emit("turn", raw=pos, detents=detents, delta=delta)
        last = pos

    if not btn.value:  # active-low
        emit("press")
        while not btn.value:
            time.sleep(0.01)
        emit("release")

    time.sleep(0.005)
