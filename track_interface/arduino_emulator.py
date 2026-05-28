# track_interface/arduino_emulator.py

import threading
import time
import serial

from serial_protocol import (
    build_version,
    build_heartbeat,
    build_input_on,
    build_input_off,
    parse_command,
    MESSAGE_RESET,
    MESSAGE_TIME_RESET,
    bytes_to_hex,
)

from gpio_runtime import (
    GPIORuntime,
)

# ============================================================
# CONFIG
# ============================================================

PORT = "/dev/pts/3"
BAUDRATE = 115200

HEARTBEAT_INTERVAL = 0.5

# ============================================================
# EMULATOR
# ============================================================

class ArduinoEmulator:

    def __init__(
        self,
        port: str,
        baudrate: int,
    ):

        self.port = port
        self.baudrate = baudrate

        self.running = False

        self.version_verified = False

        self.reset_flag = 1

        self.last_heartbeat = time.monotonic()

        self.gpio = GPIORuntime()

        self.serial = serial.Serial(
            self.port,
            self.baudrate,
            timeout=0.05,
        )

    # ========================================================

    def start(self):

        print(
            f"[EMULATOR] Starting on {self.port}"
        )

        self.running = True

        threading.Thread(
            target=self.serial_listener_loop,
            daemon=True,
        ).start()

        threading.Thread(
            target=self.heartbeat_loop,
            daemon=True,
        ).start()

    # ========================================================

    def stop(self):

        print("[EMULATOR] Stopping")

        self.running = False

        self.serial.close()

    # ========================================================
    # HEARTBEAT
    # ========================================================

    def heartbeat_loop(self):

        while self.running:

            now = time.monotonic()

            delta_us = int(
                (now - self.last_heartbeat)
                * 1_000_000
            )

            self.last_heartbeat = now

            msg = build_heartbeat(
                delta_us=delta_us,
                reset_flag=self.reset_flag,
            )

            self.send(msg)

            self.reset_flag = 0

            time.sleep(
                HEARTBEAT_INTERVAL
            )

    # ========================================================
    # SERIAL RX
    # ========================================================

    def serial_listener_loop(self):

        buffer = bytearray()

        while self.running:

            data = self.serial.read(1)

            if not data:
                continue

            byte = data[0]

            print(
                f"[RX] {hex(byte)}"
            )

            if byte == 0x3B:

                payload = bytes(buffer) + bytes([0x3B])

                print(
                    "[RX COMMAND]",
                    bytes_to_hex(payload)
                )

                self.handle_command(payload)

                buffer.clear()

            else:

                buffer.append(byte)

    # ========================================================
    # COMMAND HANDLER
    # ========================================================

    def handle_command(
        self,
        payload: bytes,
    ):

        parsed = parse_command(payload)

        # ----------------------------------------------------

        if parsed.message_type == MESSAGE_RESET:

            print(
                "[COMMAND] RESET"
            )

            self.reset_flag = 1

            version = build_version()

            self.send(version)

            self.version_verified = True

            return

        # ----------------------------------------------------

        if parsed.message_type == MESSAGE_TIME_RESET:

            print(
                "[COMMAND] TIME RESET"
            )

            self.reset_flag = 1

            return

        # ----------------------------------------------------

        print(
            "[COMMAND] UNKNOWN"
        )

    # ========================================================
    # SERIAL TX
    # ========================================================

    def send(
        self,
        payload: bytes,
    ):

        self.serial.write(payload)

        self.serial.flush()

        print(
            "[TX]",
            bytes_to_hex(payload)
        )

    # ========================================================
    # GPIO SENSOR API
    # ========================================================

    def sensor_on(
        self,
        pin: int,
    ):

        self.gpio.set_pin_high(pin)

        msg = build_input_on(
            pin=pin,
            is_digital=True,
        )

        self.send(msg)

    # ========================================================

    def sensor_off(
        self,
        pin: int,
    ):

        self.gpio.set_pin_low(pin)

        msg = build_input_off(
            pin=pin,
            is_digital=True,
        )

        self.send(msg)

    # ========================================================

    def pulse_sensor(
        self,
        pin: int,
        pulse_ms: int = 30,
    ):

        self.sensor_on(pin)

        time.sleep(
            pulse_ms / 1000.0
        )

        self.sensor_off(pin)

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    emulator = ArduinoEmulator(
        port=PORT,
        baudrate=BAUDRATE,
    )

    emulator.start()

    # --------------------------------------------------------
    # DEBUG TEST LOOP
    # --------------------------------------------------------

    while True:

        time.sleep(5)

        print(
            "\n[TEST] Simulated lap on pin 2\n"
        )

        emulator.pulse_sensor(
            pin=2,
            pulse_ms=30,
        )
