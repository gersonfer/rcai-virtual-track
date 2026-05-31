# Protocol Walkthrough — RC AI / Arduino / Python Emulator

## What This Document Covers

This document explains the complete lifecycle of a race in plain language: from the moment RC AI connects to the Arduino/emulator, through race start, lap detection, pause, restart, and shutdown.

No protocol bytes needed to follow this explanation.

---

## The Two Clocks Problem

The most important thing to understand before anything else:

> RC AI does **not** use its own clock to measure lap times.
> It uses **the Arduino's clock**, accumulated via heartbeat messages.

Every ~0.5 seconds, the emulator sends a heartbeat message that says:
> "This much time has passed since my last heartbeat."

RC AI keeps a running total of these time chunks, per lane. That total is the lap time. When a car crosses the sensor, RC AI reads the accumulated total and calls it a lap.

This means: **if the heartbeat resync fails, no laps get counted.**

---

## Phase 1: Connection Startup

### What happens physically (real Arduino):

1. RC AI opens the serial port
2. Arduino immediately boots and sends its version number, without being asked
3. RC AI reads the version and decides if the firmware is compatible

### What happens with the emulator:

1. RC AI opens the serial port and sends `RESET;`
2. Emulator receives RESET, marks itself as verified, and sends the version response
3. RC AI reads the version and proceeds

The key difference is: **the Arduino volunteers the version on boot. The emulator waits for RESET first.**
In practice this works the same way because RC AI sends RESET immediately on connect.

---

## Phase 2: Hardware Configuration

After verifying the version, RC AI sends several setup commands:

1. **Which pins to watch as inputs** (lap sensors)
2. **Which pins to control as outputs** (relays, LEDs)
3. **Which analog pins to read** (voltage sensors)
4. **Debounce timing** (how long a pin must stay stable to count as a real event)

### What the real Arduino does:

After receiving the input pin configuration, the Arduino **immediately broadcasts the current state of every configured pin**. This is an initial snapshot that tells RC AI where everything stands before the race starts.

### What the emulator does:

The emulator does not process any of these configuration commands. It does not know which pins are supposed to be inputs, and it does not broadcast an initial state snapshot.

> **This means RC AI never receives the initial state broadcast from the emulator.**

---

## Phase 3: Time Synchronization

After hardware configuration, RC AI sends a **Time Reset** command (`T;`).

### What the Time Reset does:

1. RC AI resets all internal lap timing accumulators to zero
2. RC AI sets an internal flag: "I am expecting a reset confirmation"
3. The Arduino/emulator responds by flushing the current time and marking the next heartbeat with a reset flag

### The reset confirmation handshake:

```
RC AI sends: T;
RC AI thinks: "I am waiting for reset confirmation. hwReset = 1"

Arduino sends heartbeat with reset_flag = 1
RC AI thinks: "reset_flag matches hwReset. Accepted. hwReset = 0. Timing active."

Arduino sends next heartbeat with reset_flag = 0
RC AI thinks: "Normal. Adding time to accumulators."
```

### What the emulator does:

The emulator recognizes the `T;` command but does **not**:
- Send a flush time message
- Set the reset flag on the next heartbeat

The emulator always sends `reset_flag = 1` on the very first heartbeat (the one after `start()`), then 0 forever after.

> **This is the root cause of the lap-counting problem.**

---

## Phase 4: Race Start

RC AI starts a race and sends:

1. An Extended Protocol message: `E RaceState RUNNING` (state = 4)
2. A **Time Reset** (`T;`) to synchronize the timing clock for the race start

At this moment, the timing resync handshake must succeed for laps to be counted.

If the handshake fails:

```
RC AI: hwReset = 1 (expecting confirmation)
Emulator heartbeat: reset_flag = 0 (always, after the first one)
RC AI: "reset_flag != hwReset. Mismatch! Clearing pin cache. hwReset = 0."
RC AI: "Now hwReset is 0. Next heartbeat (also 0) matches. Accepted."
RC AI: "Timing starts from this heartbeat."
```

This mismatch causes RC AI to reject the first heartbeat and resync on the second. One heartbeat interval is lost. But more critically: **the pin state cache is cleared**, and RC AI re-initializes hardware state. This causes relay state to be resent, which explains why a Pause/Restart later seems to "wake up" the system.

---

## Phase 5: Lap Detection

Under normal operation, a lap is detected as follows:

1. Time accumulates via heartbeats
2. A car physically crosses the sensor
3. Arduino detects the pin going LOW (the sensor is triggered)
4. Arduino sends: `INPUT type=Digital pin=X state=0`
5. RC AI receives the input, looks up which lane this sensor belongs to
6. RC AI reads the accumulated lap time for that lane
7. RC AI fires a lap event with that time
8. RC AI resets the accumulator for that lane

The same process happens in the emulator: `pulse_sensor()` sends `INPUT state=1` (HIGH), waits 30ms, then `INPUT state=0` (LOW). The lap is triggered on the LOW edge.

> **Important:** In the emulator, the pulse sends HIGH first, then LOW. The lap fires on the LOW. This is correct behavior.

---

## Phase 6: Pause

RC AI pauses the race:

1. Sends `E RaceState PAUSED` (state = 5)
2. Sends `T;` — the timing reset command

The same time resync handshake must happen. After Pause, the lap accumulators are reset. When the race resumes, new timing begins cleanly.

---

## Phase 7: Restart

RC AI resumes the race:

1. Sends `E RaceState RESTARTED` (state = 3)
2. Sends `T;` again

This triggers another resync handshake. After this second `T;` during Pause/Restart, the resync happens at a point where the emulator happens to correctly send `reset_flag = 0` in its subsequent heartbeats. Since `hwReset` was already cleared from the previous mismatch, the heartbeat is accepted and timing resumes.

> This explains the observed symptom: "laps work after Pause/Restart but not at race start."

---

## Phase 8: Heat End / Race Over

RC AI sends:
- `E RaceState HEAT_ENDED` (state = 6)
- Relays turned off: `OD pin 0` for each lane relay
- `E RaceState RACE_ENDED` (state = 7) when all heats complete

The emulator handles relay OFF correctly (updates `output_states`). No lap generation issues at this stage.

---

## Summary: The Lap-Counting Problem Explained Simply

| Stage | Expected Behavior | Emulator Behavior |
|---|---|---|
| Boot | Sends VERSION immediately | Waits for RESET first |
| Pin Config | Broadcasts initial pin states | Does nothing |
| Time Reset (race start) | Sends flush + next heartbeat with reset_flag=1 | Does nothing extra; reset_flag stays 0 |
| Heartbeat after Time Reset | reset_flag = 1 (confirming reset) | reset_flag = 0 (mismatch) |
| RC AI reaction | Accepts resync, timing begins | Rejects heartbeat, clears pin cache, tries to re-initialize |
| Lap counting | Works from race start | Broken until Pause/Restart triggers second sync opportunity |
