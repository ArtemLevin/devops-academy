#!/usr/bin/env python3
"""Урок 05. Read-only measurements of memory and process properties on Linux."""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import time


def parse_kib_fields(contents: str) -> dict[str, int]:
    """Read /proc/meminfo lines containing a number in KiB."""
    values: dict[str, int] = {}
    for line in contents.splitlines():
        if ':' not in line:
            continue
        key, tail = line.split(':', 1)
        number = tail.strip().split()
        if number and number[0].isdigit():
            values[key] = int(number[0])
    return values


def parse_vmstat(contents: str) -> dict[str, int]:
    result: dict[str, int] = {}
    for line in contents.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[0] in {'pswpin', 'pswpout'}:
            result[parts[0]] = int(parts[1])
    return result


def sample(delay: float = 1.0) -> dict[str, object]:
    mem = parse_kib_fields(Path('/proc/meminfo').read_text())
    first = parse_vmstat(Path('/proc/vmstat').read_text())
    time.sleep(delay)
    second = parse_vmstat(Path('/proc/vmstat').read_text())
    mode = Path.home().stat().st_mode
    result = {
        'pid': os.getpid(), 'ppid': os.getppid(),
        'home_permission_bits': oct(stat.S_IMODE(mode)),
        'mem_available_mib': round(mem.get('MemAvailable', 0) / 1024, 1),
        'swap_used_mib': round((mem.get('SwapTotal', 0) - mem.get('SwapFree', 0)) / 1024, 1),
        'swap_in_pages_delta': max(0, second.get('pswpin', 0) - first.get('pswpin', 0)),
        'swap_out_pages_delta': max(0, second.get('pswpout', 0) - first.get('pswpout', 0)),
        'interval_seconds': delay,
    }
    return result


def main() -> None:
    if not Path('/proc/meminfo').exists() or not Path('/proc/vmstat').exists():
        raise SystemExit('Нужен Linux с файловой системой /proc.')
    print(json.dumps(sample(), ensure_ascii=False, indent=2))
    print('\nЭто единичная выборка. Для диагноза memory pressure сравните несколько измерений.')
    print('Родительский PID не задаёт автоматически владельца и права дочернего процесса.')


if __name__ == '__main__':
    main()
