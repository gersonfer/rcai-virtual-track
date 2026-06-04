pi@rpi4:~/projects/rcai-virtual-track $ python main.py
[PROFILE_MANAGER] Loaded 4 profiles
[EMULATOR] Starting on /dev/pts/2
[RELAYLOGIC] Configured relay mode at startup: normally_closed
[LANE_ASSIGNMENT] Lane 1 -> ferrari_499p
[LANE_ASSIGNMENT] Lane 2 -> porsche_963
[LANE_ASSIGNMENT] Lane 3 -> toyota_gr010
[LANE_ASSIGNMENT] Lane 4 -> cadillac_vseriesr
[RACE_RUNTIME] Starting runtime
[LANE 1] Runtime started
[LANE 2] Runtime started
[LANE 3] Runtime started
[LANE 1] STATE -> STOPPED
[LANE 2] STATE -> STOPPED
[LANE 3] STATE -> STOPPED

[LANE 4] Runtime started
========================================
[LANE 4] STATE -> STOPPED
VIRTUAL SLOT PLATFORM
========================================

========== LANE ASSIGNMENTS ==========
Lane 1 -> ferrari_499p
Lane 2 -> porsche_963
Lane 3 -> toyota_gr010
Lane 4 -> cadillac_vseriesr
======================================

Running...
CTRL+C to stop

[COMMAND] RESET
[COMMAND] PIN_MODE_READ
[PIN MAP] Input: physical sensor 2 -> protocol D2
[PIN MAP] Input: physical sensor 3 -> protocol D3
[PIN MAP] Input: physical sensor 4 -> protocol D4
[PIN MAP] Input: physical sensor 5 -> protocol D5
[GPIO] PIN 2 -> HIGH
[GPIO] PIN 3 -> HIGH
[GPIO] PIN 4 -> HIGH
[GPIO] PIN 5 -> HIGH
[COMMAND] PIN_MODE_WRITE
[PIN MAP] Output: protocol D6 -> physical relay 6
[PIN MAP] Output: protocol D7 -> physical relay 7
[PIN MAP] Output: protocol D8 -> physical relay 8
[PIN MAP] Output: protocol D9 -> physical relay 9
[COMMAND] UNKNOWN payload=0x70 0x00 0x3B
[COMMAND] UNKNOWN payload=0x64 0x00 0x32 0x00 0x32 0x3B
[COMMAND] TIME RESET
[GAP001] T; received at +0 ms (reset_flag currently=1)
[COMMAND] TIME RESET
[GAP001] T; received at +0 ms (reset_flag currently=0)
[LANE 1] STATE -> POWERED
[LANE 2] STATE -> POWERED
[LANE 4] STATE -> POWERED
[LANE 3] STATE -> POWERED
[LANE 1] LAP Ferrari 499P 4.091s
[GPIO] PIN 2 -> HIGH
[GPIO] PIN 2 -> LOW
[LANE 4] LAP Cadillac V-Series.R 4.354s
[GPIO] PIN 5 -> HIGH
[GPIO] PIN 5 -> LOW
[LANE 3] LAP Toyota GR010 4.365s
[GPIO] PIN 4 -> HIGH
[GPIO] PIN 4 -> LOW
[LANE 2] LAP Porsche 963 4.519s
[GPIO] PIN 3 -> HIGH
[GPIO] PIN 3 -> LOW
[LANE 1] LAP Ferrari 499P 4.139s
[GPIO] PIN 2 -> HIGH
[GPIO] PIN 2 -> LOW
[LANE 3] LAP Toyota GR010 4.279s
[GPIO] PIN 4 -> HIGH
[GPIO] PIN 4 -> LOW
[LANE 4] LAP Cadillac V-Series.R 4.484s
[GPIO] PIN 5 -> HIGH
[GPIO] PIN 5 -> LOW
[LANE 2] LAP Porsche 963 4.317s
[GPIO] PIN 3 -> HIGH
[GPIO] PIN 3 -> LOW
[LANE 1] LAP Ferrari 499P 4.222s
[GPIO] PIN 2 -> HIGH
[GPIO] PIN 2 -> LOW
[LANE 3] LAP Toyota GR010 4.330s
[GPIO] PIN 4 -> HIGH
[GPIO] PIN 4 -> LOW
[LANE 4] LAP Cadillac V-Series.R 4.545s
[GPIO] PIN 5 -> HIGH
[GPIO] PIN 5 -> LOW
[LANE 2] LAP Porsche 963 4.544s
[GPIO] PIN 3 -> HIGH
[GPIO] PIN 3 -> LOW
[LANE 1] LAP Ferrari 499P 4.268s
[GPIO] PIN 2 -> HIGH
[GPIO] PIN 2 -> LOW
[LANE 3] LAP Toyota GR010 4.450s
[GPIO] PIN 4 -> HIGH
[GPIO] PIN 4 -> LOW
[LANE 4] LAP Cadillac V-Series.R 4.442s
[GPIO] PIN 5 -> HIGH
[GPIO] PIN 5 -> LOW
[LANE 2] LAP Porsche 963 4.468s
[GPIO] PIN 3 -> HIGH
[GPIO] PIN 3 -> LOW
[LANE 1] LAP Ferrari 499P 4.256s
[GPIO] PIN 2 -> HIGH
[GPIO] PIN 2 -> LOW
[LANE 3] LAP Toyota GR010 4.303s
[GPIO] PIN 4 -> HIGH
[GPIO] PIN 4 -> LOW
[LANE 4] LAP Cadillac V-Series.R 4.382s
[GPIO] PIN 5 -> HIGH
[GPIO] PIN 5 -> LOW
[LANE 2] LAP Porsche 963 4.581s
[GPIO] PIN 3 -> HIGH
[GPIO] PIN 3 -> LOW
[LANE 4] STATE -> COASTING (Power Lost)
[LANE 3] STATE -> COASTING (Power Lost)
[COASTING]
lane=4
lap_time=4.557
elapsed=2.906
remaining=1.651
coasting_duration=0.500
[COASTING]
lane=3
lap_time=4.335
elapsed=3.357
remaining=0.978
coasting_duration=0.500[LANE 2] STATE -> COASTING (Power Lost)

[LANE 1] STATE -> COASTING (Power Lost)
[COASTING]
lane=2
lap_time=4.443
elapsed=2.606
remaining=1.837
coasting_duration=0.500
[COASTING]
lane=1
lap_time=7.287
elapsed=4.110
remaining=3.177
coasting_duration=0.500
[COASTING RESULT] MOMENTUM_LOST
[COASTING RESULT] MOMENTUM_LOST
[LANE 4] STATE -> STOPPED (Momentum Lost)
[LANE 3] STATE -> STOPPED (Momentum Lost)
[COASTING RESULT] MOMENTUM_LOST
[LANE 2] STATE -> STOPPED (Momentum Lost)
[COASTING RESULT] MOMENTUM_LOST
[LANE 1] STATE -> STOPPED (Momentum Lost)
[COMMAND] TIME RESET
[GAP001] T; received at +0 ms (reset_flag currently=0)
[LANE 4] STATE -> POWERED
[LANE 2] STATE -> POWERED
[LANE 3] STATE -> POWERED
[LANE 1] STATE -> POWERED
[LANE 3] LAP Toyota GR010 4.202s
[GPIO] PIN 4 -> HIGH
[GPIO] PIN 4 -> LOW
[LANE 1] LAP Ferrari 499P 4.246s
[GPIO] PIN 2 -> HIGH
[GPIO] PIN 2 -> LOW
[LANE 4] LAP Cadillac V-Series.R 4.451s
[GPIO] PIN 5 -> HIGH
[LANE 2] LAP Porsche 963 4.429s
[GPIO] PIN 3 -> HIGH
[GPIO] PIN 3 -> LOW
[GPIO] PIN 5 -> LOW
[LANE 3] LAP Toyota GR010 4.310s
[GPIO] PIN 4 -> HIGH
[GPIO] PIN 4 -> LOW
[LANE 1] LAP Ferrari 499P 4.306s
[GPIO] PIN 2 -> HIGH
[GPIO] PIN 2 -> LOW
[LANE 2] LAP Porsche 963 4.455s
[GPIO] PIN 3 -> HIGH
[GPIO] PIN 3 -> LOW
[LANE 4] LAP Cadillac V-Series.R 4.623s
[GPIO] PIN 5 -> HIGH
[GPIO] PIN 5 -> LOW
[LANE 3] STATE -> COASTING (Power Lost)
[LANE 4] STATE -> COASTING (Power Lost)
[COASTING]
lane=3
lap_time=4.231
elapsed=4.060
remaining=0.171
coasting_duration=0.500
[COASTING]
lane=4
lap_time=4.349
elapsed=3.458
remaining=0.891
coasting_duration=0.500
[LANE 2] STATE -> COASTING (Power Lost)
[COASTING]
lane=2
lap_time=4.255
elapsed=3.661
remaining=0.593
coasting_duration=0.500
[LANE 1] STATE -> COASTING (Power Lost)
[COASTING]
lane=1
lap_time=4.251
elapsed=4.012
remaining=0.238
coasting_duration=0.500
[COASTING RESULT] LAP_COMPLETED
[LANE 3] LAP Toyota GR010 4.231s
[GPIO] PIN 4 -> HIGH
[GPIO] PIN 4 -> LOW
[LANE 3] STATE -> STOPPED
[COASTING RESULT] LAP_COMPLETED
[LANE 1] LAP Ferrari 499P 4.251s
[GPIO] PIN 2 -> HIGH
[GPIO] PIN 2 -> LOW
[LANE 1] STATE -> STOPPED
[COASTING RESULT] MOMENTUM_LOST
[LANE 4] STATE -> STOPPED (Momentum Lost)
[COASTING RESULT] MOMENTUM_LOST
[LANE 2] STATE -> STOPPED (Momentum Lost)
[COMMAND] TIME RESET
[GAP001] T; received at +0 ms (reset_flag currently=0)
[LANE 2] STATE -> POWERED
[LANE 4] STATE -> POWERED
[LANE 3] STATE -> POWERED
[LANE 1] STATE -> POWERED
[LANE 3] STATE -> COASTING (Power Lost)
[COASTING]
lane=3
lap_time=4.347
elapsed=3.257
remaining=1.090
coasting_duration=0.500
[LANE 1] STATE -> COASTING (Power Lost)
[COASTING]
lane=1
lap_time=4.307
elapsed=3.206
remaining=1.100
coasting_duration=0.500
[LANE 2] STATE -> COASTING (Power Lost)
[LANE 4] STATE -> COASTING (Power Lost)
[COASTING]
lane=2
lap_time=4.605
elapsed=3.308
remaining=1.298
coasting_duration=0.500
[COASTING]
lane=4
lap_time=4.397
elapsed=3.308
remaining=1.090
coasting_duration=0.500
[COASTING RESULT] MOMENTUM_LOST
[LANE 3] STATE -> STOPPED (Momentum Lost)
[COASTING RESULT] MOMENTUM_LOST
[LANE 1] STATE -> STOPPED (Momentum Lost)
[COASTING RESULT] MOMENTUM_LOST
[LANE 2] STATE -> STOPPED (Momentum Lost)
[COASTING RESULT] MOMENTUM_LOST
[LANE 4] STATE -> STOPPED (Momentum Lost)
[COMMAND] TIME RESET
[GAP001] T; received at +0 ms (reset_flag currently=0)
[LANE 3] STATE -> POWERED
[LANE 1] STATE -> POWERED
[LANE 2] STATE -> POWERED
[LANE 4] STATE -> POWERED
[LANE 3] LAP Toyota GR010 4.188s
[GPIO] PIN 4 -> HIGH
[GPIO] PIN 4 -> LOW
[LANE 1] LAP Ferrari 499P 4.266s
[GPIO] PIN 2 -> HIGH
[LANE 2] LAP Porsche 963 4.278s
[GPIO] PIN 3 -> HIGH
[GPIO] PIN 2 -> LOW
[GPIO] PIN 3 -> LOW
[LANE 4] LAP Cadillac V-Series.R 4.400s
[GPIO] PIN 5 -> HIGH
[GPIO] PIN 5 -> LOW
[LANE 3] LAP Toyota GR010 4.189s
[GPIO] PIN 4 -> HIGH
[GPIO] PIN 4 -> LOW
[LANE 1] LAP Ferrari 499P 4.199s
[GPIO] PIN 2 -> HIGH
[GPIO] PIN 2 -> LOW
[LANE 2] LAP Porsche 963 4.294s
[GPIO] PIN 3 -> HIGH
[GPIO] PIN 3 -> LOW
[LANE 4] LAP Cadillac V-Series.R 4.291s
[GPIO] PIN 5 -> HIGH
[GPIO] PIN 5 -> LOW
[LANE 3] LAP Toyota GR010 4.251s
[GPIO] PIN 4 -> HIGH
[GPIO] PIN 4 -> LOW
[LANE 1] LAP Ferrari 499P 4.285s
[GPIO] PIN 2 -> HIGH
[GPIO] PIN 2 -> LOW
[LANE 2] LAP Porsche 963 4.438s
[GPIO] PIN 3 -> HIGH
[GPIO] PIN 3 -> LOW
[LANE 4] LAP Cadillac V-Series.R 4.364s
[GPIO] PIN 5 -> HIGH
[GPIO] PIN 5 -> LOW
[LANE 3] LAP Toyota GR010 4.185s
[GPIO] PIN 4 -> HIGH
[GPIO] PIN 4 -> LOW
[LANE 1] LAP Ferrari 499P 4.219s
[GPIO] PIN 2 -> HIGH
[GPIO] PIN 2 -> LOW
[LANE 2] LAP Porsche 963 4.222s
[GPIO] PIN 3 -> HIGH
[GPIO] PIN 3 -> LOW
[LANE 4] LAP Cadillac V-Series.R 4.494s
[GPIO] PIN 5 -> HIGH
[GPIO] PIN 5 -> LOW
[LANE 1] STATE -> COASTING (Power Lost)
[COASTING]
lane=1
lap_time=4.115
elapsed=1.753
remaining=2.361
coasting_duration=0.500
[LANE 3] STATE -> COASTING (Power Lost)
[COASTING]
lane=3
lap_time=4.316
elapsed=1.953
remaining=2.363
coasting_duration=0.500
[LANE 4] STATE -> COASTING (Power Lost)
[LANE 2] STATE -> COASTING (Power Lost)
[COASTING]
lane=4
lap_time=4.445
elapsed=1.203
remaining=3.242
coasting_duration=0.500
[COASTING]
lane=2
lap_time=4.347
elapsed=1.503
remaining=2.844
coasting_duration=0.500
[COASTING RESULT] MOMENTUM_LOST
[COASTING RESULT] MOMENTUM_LOST
[LANE 1] STATE -> STOPPED (Momentum Lost)
[LANE 3] STATE -> STOPPED (Momentum Lost)
[COASTING RESULT] MOMENTUM_LOST
[COASTING RESULT] MOMENTUM_LOST
[LANE 4] STATE -> STOPPED (Momentum Lost)
[LANE 2] STATE -> STOPPED (Momentum Lost)

