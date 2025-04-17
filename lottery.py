import time
import threading
import random
import json
import os
from datetime import datetime, timedelta

# Global Variables
participants = set()
log_filename = "lottery_log.txt"
auto_save_interval = 300  # in seconds (5 mins)
registration_start = datetime.now()
registration_end = registration_start + timedelta(hours=1)
extended = False
lock = threading.Lock()

# Helper Functio
def log_event(message):
    with open(log_filename, 'a') as log_file:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file.write(f"[{timestamp}] {message}\n")

def auto_save():
    while datetime.now() < registration_end:
        time.sleep(auto_save_interval)
        with lock:
            with open('backup.json', 'w') as f:
                json.dump(list(participants), f)
            log_event("Auto-saved participant list.")

def display_timer():
    while datetime.now() < registration_end:
        time_left = registration_end - datetime.now()
        if time_left.total_seconds() % 600 < 1:  # every 10 mins
            mins = int(time_left.total_seconds() / 60)
            print(f"\n[INFO] {mins} minutes left to register.")
        time.sleep(60)

def is_valid_username(username):
    return username.isalnum() and username.strip() != ""

def register_users():
    global registration_end, extended
    print("Registration is open for 1 hour. Please enter your username:")
    while datetime.now() < registration_end:
        username = input("Enter username: ").strip()
        with lock:
            if not is_valid_username(username):
                print("Invalid username. Must be alphanumeric and non-empty.")
                continue
            if username in participants:
                print("Username already registered.")
                continue
            participants.add(username)
            log_event(f"User registered: {username}")
            print(f"[REGISTERED] Current count: {len(participants)}")
        
        if len(participants) < 5 and not extended and datetime.now() > registration_start + timedelta(hours=1):
            registration_end += timedelta(minutes=30)
            extended = True
            print("\n[INFO] Less than 5 users, extending registration by 30 minutes.")


def draw_winner():
    if len(participants) == 0:
        print("\n[EXIT] No users registered. Lottery cannot proceed.")
        log_event("Program exited due to no participants.")
        return
    winner = random.choice(list(participants))
    log_event(f"Winner selected: {winner}")
    print("\n========================")
    print("🎉 Lottery Winner 🎉")
    print(f"Winner: {winner}")
    print(f"Total Participants: {len(participants)}")
    print("========================")

# Main Execution
if __name__ == '__main__':
    print("\n[START] Lottery system started at", registration_start.strftime('%H:%M:%S'))
    log_event("Lottery system started.")

    # Load backup if available
    if os.path.exists('backup.json'):
        with open('backup.json', 'r') as f:
            participants = set(json.load(f))
        print("[INFO] Loaded backup participants.")

    # Threads
    save_thread = threading.Thread(target=auto_save, daemon=True)
    timer_thread = threading.Thread(target=display_timer, daemon=True)

    save_thread.start()
    timer_thread.start()

    try:
        register_users()
    except KeyboardInterrupt:
        print("\n[WARNING] Interrupted by user.")
    finally:
        draw_winner()
        log_event("Lottery system finished.")
