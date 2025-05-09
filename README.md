# Raspberry Pi E-Paper Display Scheduler

This project runs a schedule-based display on a Waveshare 7.5-inch V2 e-ink screen using a Raspberry Pi.

## Features
- Multi-room schedule pulled from `schedule.csv`
- Auto-select by room using `room_config.txt`
- Displays:
  - Header: University of Portland Biology
  - Current class
  - Class title
  - Instructor
  - Time
- Rotates PNG events when no class is active

## Setup

1. Install Raspberry Pi OS (Lite or Full)
2. Enable SPI:
    ```
    sudo raspi-config → Interface Options → SPI → Enable
    ```
3. Clone this repo:
    ```
    git clone <your_repo_url>
    ```
4. Create virtual environment:
    ```
    python3 -m venv waveshare-env
    source waveshare-env/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    ```
5. Install Waveshare Python driver:
    ```
    cd ~/e-Paper/RaspberryPi_JetsonNano/python
    pip install .
    ```

## Running

