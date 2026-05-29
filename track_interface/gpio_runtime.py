# track_interface/gpio_runtime.py

import threading
import time
from dataclasses import dataclass
from typing import Dict

# ============================================================
# GPIO STATE
# ============================================================

GPIO_LOW = 0
GPIO_HIGH = 1

# ============================================================
# GPIO PIN MODEL
# ============================================================

@dataclass
class GPIOPin:

    pin_number: int
    state: int = GPIO_LOW

# ============================================================
# GPIO RUNTIME
# ============================================================

class GPIORuntime:

    def __init__(self):

        self._pins: Dict[int, GPIOPin] = {}

        self._lock = threading.RLock()

    # ========================================================

    def ensure_pin(
        self,
        pin_number: int,
    ):

        with self._lock:

            if pin_number not in self._pins:

                self._pins[pin_number] = GPIOPin(
                    pin_number=pin_number,
                    state=GPIO_LOW,
                )

    # ========================================================

    def set_pin_high(
        self,
        pin_number: int,
    ):

        with self._lock:

            self.ensure_pin(pin_number)

            self._pins[pin_number].state = GPIO_HIGH

            print(
                f"[GPIO] PIN {pin_number} -> HIGH"
            )

    # ========================================================

    def set_pin_low(
        self,
        pin_number: int,
    ):

        with self._lock:

            self.ensure_pin(pin_number)

            self._pins[pin_number].state = GPIO_LOW

            print(
                f"[GPIO] PIN {pin_number} -> LOW"
            )

    # ========================================================

    def get_pin_state(
        self,
        pin_number: int,
    ) -> int:

        with self._lock:

            self.ensure_pin(pin_number)

            return self._pins[pin_number].state

    # ========================================================

    def pulse_pin(
        self,
        pin_number: int,
        pulse_ms: int = 30,
    ):

        self.set_pin_high(pin_number)

        time.sleep(
            pulse_ms / 1000.0
        )

        self.set_pin_low(pin_number)

    # ========================================================

    def snapshot(self):

        with self._lock:

            return {
                pin: gpio.state
                for pin, gpio in self._pins.items()
            }

    # ========================================================

    def dump(self):

        snapshot = self.snapshot()

        print("========== GPIO STATE ==========")

        for pin in sorted(snapshot.keys()):

            state = snapshot[pin]

            label = (
                "HIGH"
                if state == GPIO_HIGH
                else "LOW"
            )

            print(
                f"PIN {pin}: {label}"
            )

        print("================================")

# ============================================================
# DEBUG
# ============================================================

if __name__ == "__main__":

    gpio = GPIORuntime()

    gpio.set_pin_high(2)

    gpio.set_pin_low(2)

    gpio.pulse_pin(
        pin_number=3,
        pulse_ms=100,
    )

    gpio.dump()
