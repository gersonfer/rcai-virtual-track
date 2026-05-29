#!/usr/bin/env python3

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

TRACK_JSON = Path("config/track.json")
SOCAT_JSON = Path("runtime/socat.json")


def update_track_json(track_port):

    with open(
        TRACK_JSON,
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    data["serial"]["port"] = track_port

    with open(
        TRACK_JSON,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            indent=2,
        )

    print(
        f"[CONFIG] track.json updated -> {track_port}"
    )


def save_socat_info(
    pid,
    rcai_port,
    track_port,
):

    SOCAT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = {
        "pid": pid,
        "rcai_port": rcai_port,
        "track_port": track_port,
        "created_at": datetime.now().isoformat(),
    }

    with open(
        SOCAT_JSON,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
        )


def find_socat_pid():

    result = subprocess.run(
        ["pgrep", "-af", "socat"],
        capture_output=True,
        text=True,
    )

    pids = []

    for line in result.stdout.splitlines():

        if not line.strip():
            continue

        parts = line.split(
            maxsplit=1
        )

        if len(parts) != 2:
            continue

        pid = parts[0]
        command = parts[1]

        if command.startswith(
            "socat -d -d pty,raw,echo=0 pty,raw,echo=0"
        ):
            pids.append(pid)

    return pids


def get_pts_from_pid(pid):

    result = subprocess.run(
        ["lsof", "-p", str(pid)],
        capture_output=True,
        text=True,
    )

    pts = []

    for line in result.stdout.splitlines():

        match = re.search(
            r"\s([6-9]\d*)u\s+CHR.*(/dev/pts/\d+)$",
            line,
        )

        if match:
            pts.append(
                match.group(2)
            )

    return sorted(
        list(set(pts)),
        key=lambda x: int(
            x.split("/")[-1]
        ),
    )


def start_socat():

    process = subprocess.Popen(
        [
            "socat",
            "-d",
            "-d",
            "pty,raw,echo=0",
            "pty,raw,echo=0",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    pts = []

    start_time = time.time()

    while (
        time.time() - start_time
    ) < 5:

        line = (
            process.stdout.readline()
        )

        if not line:
            continue

        print(line.rstrip())

        match = re.search(
            r"PTY is (/dev/pts/\d+)",
            line,
        )

        if match:
            pts.append(
                match.group(1)
            )

        if len(pts) == 2:
            break

    if len(pts) != 2:
        raise RuntimeError(
            "Could not determine PTY pair created by socat."
        )

    return (
        process.pid,
        sorted(
            pts,
            key=lambda p: int(
                p.split("/")[-1]
            ),
        ),
    )


def main():

    pids = find_socat_pid()

    if len(pids) > 1:

        print("")
        print("ERROR")
        print(
            "More than one socat process found:"
        )
        print("")

        for pid in pids:
            print(
                f"PID {pid}"
            )

        sys.exit(1)

    if len(pids) == 1:

        print("")
        print(
            "SOCAT already running"
        )
        print("")

        socat_pid = pids[0]

        pts = get_pts_from_pid(
            socat_pid
        )

        if len(pts) != 2:

            print(
                "Could not determine PTY pair "
                "from existing socat."
            )

            sys.exit(1)

    else:

        print("")
        print(
            "No active socat found"
        )
        print(
            "Starting socat..."
        )
        print("")

        socat_pid, pts = (
            start_socat()
        )

    rcai_port = pts[0]
    track_port = pts[1]

    update_track_json(
        track_port
    )

    save_socat_info(
        pid=socat_pid,
        rcai_port=rcai_port,
        track_port=track_port,
    )

    print("")
    print(
        "================================"
    )
    print("RC AI PORT")
    print(
        "================================"
    )
    print(rcai_port)

    print("")
    print(
        "================================"
    )
    print(
        "VIRTUAL TRACK PORT"
    )
    print(
        "================================"
    )
    print(track_port)
    print("")


if __name__ == "__main__":
    main()