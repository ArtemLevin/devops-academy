#!/usr/bin/env python3
"""Урок 04. Read-only evidence of the Linux / WSL environment."""
from __future__ import annotations

import json
import os
from pathlib import Path
import platform
import shutil
import subprocess


def parse_os_release(data: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in data.splitlines():
        if "=" not in line or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        result[key] = value.strip().strip('"')
    return result


def diagnose() -> dict[str, object]:
    release = Path('/etc/os-release')
    distro = parse_os_release(release.read_text(encoding='utf-8')) if release.exists() else {}
    kernel = platform.release()
    wsl = 'microsoft' in kernel.lower() or bool(os.environ.get('WSL_DISTRO_NAME'))
    docker_cli = shutil.which('docker') is not None
    docker_engine = 'не проверялся'
    if docker_cli:
        try:
            proc = subprocess.run(['docker', 'info', '--format', '{{.ServerVersion}}'],
                                  capture_output=True, text=True, timeout=5, check=False)
            docker_engine = proc.stdout.strip() if proc.returncode == 0 and proc.stdout.strip() else 'недоступен'
        except (OSError, subprocess.TimeoutExpired):
            docker_engine = 'недоступен'
    return {
        'os': distro.get('PRETTY_NAME', platform.system()),
        'wsl_detected': wsl,
        'workdir': str(Path.cwd()),
        'home': str(Path.home()),
        'uid': os.getuid() if hasattr(os, 'getuid') else None,
        'docker_cli_available': docker_cli,
        'docker_engine_version': docker_engine,
    }


def main() -> None:
    report = diagnose()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print('\nПроверка: рабочий каталог и домашний каталог — разные понятия.')
    print('Важно: наличие Docker CLI само по себе не доказывает доступность Docker Engine.')
    print('Никаких файлов или системных настроек программа не изменяла.')


if __name__ == '__main__':
    main()
