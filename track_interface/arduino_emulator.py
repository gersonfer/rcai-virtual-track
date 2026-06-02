# track_interface/arduino_emulator.py

import threading
import time
import serial

from track_interface.serial_protocol import (
    build_version,
    build_heartbeat,
    build_input_on,
    build_input_off,
    parse_command,
    MESSAGE_RESET,
    MESSAGE_TIME_RESET,
    MESSAGE_PIN_WRITE,
    MESSAGE_PIN_MODE_READ,
    MESSAGE_PIN_MODE_WRITE,
    bytes_to_hex,
)

from track_interface.gpio_runtime import (
    GPIORuntime,
)

# ============================================================
# CONFIG
# ============================================================

HEARTBEAT_INTERVAL = 0.5
DEBUG_SERIAL = False

# Set to True to enable GAP-001 timing instrumentation.
# Logs every T; reception and every heartbeat with reset_flag and ms since last T;.
DEBUG_GAP001 = True

# ============================================================
# EMULATOR
# ============================================================

class ArduinoEmulator:

    def __init__(
        self,
        port: str,
        baudrate: int,
        lanes_config: list = None,
    ):

        self.port = port
        self.baudrate = baudrate
        self.lanes_config = lanes_config or []

        self.running = False

        self.version_verified = False

        self.reset_flag = 1

        # GAP-001 instrumentation: tracks when the last T; was received.
        self._last_time_reset_ts = None

        self.last_heartbeat = time.monotonic()

        self.gpio = GPIORuntime()

        self.output_states = {}

        self.input_pin_map = {}

        self.output_pin_map = {}

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

            current_reset_flag = self.reset_flag

            msg = build_heartbeat(
                delta_us=delta_us,
                reset_flag=current_reset_flag,
            )

            self.send(msg)

            # GAP-001 instrumentation
            if DEBUG_GAP001:
                if self._last_time_reset_ts is not None:
                    elapsed_ms = (now - self._last_time_reset_ts) * 1000
                    print(
                        f"[GAP001] HEARTBEAT sent "
                        f"+{elapsed_ms:.1f}ms after T; "
                        f"reset_flag={current_reset_flag}"
                    )
                else:
                    print(
                        f"[GAP001] HEARTBEAT sent "
                        f"(no T; received yet) "
                        f"reset_flag={current_reset_flag}"
                    )

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

            if DEBUG_SERIAL:
                print(
                    f"[RX] {hex(byte)}"
                )

            if byte == 0x3B:

                payload = bytes(buffer) + bytes([0x3B])

                if DEBUG_SERIAL:
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

        if DEBUG_SERIAL:
            print(
                "[COMMAND RAW]",
                bytes_to_hex(payload)
            )

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

            # GAP-001 instrumentation
            if DEBUG_GAP001:
                self._last_time_reset_ts = time.monotonic()
                print(
                    "[GAP001] T; received at +0 ms "
                    f"(reset_flag currently={self.reset_flag})"
                )

            self.reset_flag = 1

            return

        # ----------------------------------------------------

        if parsed.message_type == MESSAGE_PIN_MODE_READ:

            print(
                "[COMMAND] PIN_MODE_READ"
            )

            pins = parsed.pins or []

            for i, proto_idx in enumerate(pins):

                if i < len(self.lanes_config):

                    physical_pin = self.lanes_config[i]["sensor_pin"]

                    self.input_pin_map[physical_pin] = proto_idx

                    print(
                        f"[PIN MAP] Input: "
                        f"physical sensor {physical_pin} "
                        f"-> protocol D{proto_idx}"
                    )

            for physical_pin, proto_idx in self.input_pin_map.items():

                self.gpio.set_pin_high(physical_pin)

                msg = build_input_on(
                    pin=proto_idx,
                    is_digital=True,
                )

                self.send(msg)

            return

        # ----------------------------------------------------

        if parsed.message_type == MESSAGE_PIN_MODE_WRITE:

            print(
                "[COMMAND] PIN_MODE_WRITE"
            )

            pins = parsed.pins or []

            for i, proto_idx in enumerate(pins):

                if i < len(self.lanes_config):

                    physical_pin = self.lanes_config[i]["relay_pin"]

                    self.output_pin_map[proto_idx] = physical_pin

                    print(
                        f"[PIN MAP] Output: "
                        f"protocol D{proto_idx} "
                        f"-> physical relay {physical_pin}"
                    )

            return

        # ----------------------------------------------------

        if parsed.message_type == MESSAGE_PIN_WRITE:

            proto_pin = parsed.pin
            state = bool(parsed.state)

            if proto_pin in self.output_pin_map:
                physical_pin = self.output_pin_map[proto_pin]
            else:
                physical_pin = proto_pin

            self.output_states[physical_pin] = state

            state_str = "ON" if state else "OFF"
            
            print(
                f"[OUTPUT] PIN {physical_pin} "
                f"(proto D{proto_pin}) -> {state_str}"
            )

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

        if DEBUG_SERIAL:
            print(
                "[TX]",
                bytes_to_hex(payload)
            )

    # ========================================================
    # OUTPUT API
    # ========================================================

    def get_output_state(
        self,
        pin: int,
    ) -> bool:

        return self.output_states.get(pin, False)

    # ========================================================

    def is_lane_powered(
        self,
        relay_pin: int,
    ) -> bool:

        return self.get_output_state(relay_pin)

    # ========================================================
    # GPIO SENSOR API
    # ========================================================

    def sensor_on(
        self,
        pin: int,
    ):

        self.gpio.set_pin_high(pin)

        proto_pin = self.input_pin_map.get(pin, pin)

        msg = build_input_on(
            pin=proto_pin,
            is_digital=True,
        )

        self.send(msg)

    # ========================================================

    def sensor_off(
        self,
        pin: int,
    ):

        self.gpio.set_pin_low(pin)

        proto_pin = self.input_pin_map.get(pin, pin)

        msg = build_input_off(
            pin=proto_pin,
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

    import json
    import os

    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config",
        "track.json",
    )

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    emulator = ArduinoEmulator(
        port=config["serial"]["port"],
        baudrate=config["serial"]["baudrate"],
        lanes_config=config.get("lanes", []),
    )

    emulator.start()

    emulator.output_states[22] = True
    print(f"is_lane_powered(22) -> {emulator.is_lane_powered(22)}")

    emulator.output_states[22] = False
    print(f"is_lane_powered(22) -> {emulator.is_lane_powered(22)}")

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
