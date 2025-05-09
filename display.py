import csv
import os
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
import pytz
from waveshare_epd import epd7in5_V2

# === CONFIG ===
CONFIG_FILE = 'room_config.txt'
CSV_FILE = 'schedule.csv'
EVENT_FOLDER = 'events'
FONT_PATH = '/home/pi/display/fonts/Montserrat-Regular.ttf'
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480
HEADER_TEXT = "University of Portland Biology"

# === READ ROOM ID ===
def load_room_id():
    try:
        with open(CONFIG_FILE, 'r') as f:
            room_id = f.read().strip()
            print(f"🛡️ Loaded room ID: {room_id}")
            return room_id
    except Exception as e:
        print(f"⚠ Error reading {CONFIG_FILE}: {e}")
        return None

# === LOAD SCHEDULE ===
def load_schedule(room_id):
    try:
        with open(CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            schedule = [row for row in reader if row['room'] == room_id]
            return schedule
    except Exception as e:
        print(f"⚠ Error reading {CSV_FILE}: {e}")
        return []

# === GET CURRENT CLASS ===
def get_current_class(schedule):
    tz = pytz.timezone('US/Pacific')
    now = datetime.now(tz)
    current_day = now.strftime('%A')
    current_time = now.strftime('%H:%M')

    for slot in schedule:
        if slot['day'] == current_day:
            if slot['start_time'] <= current_time < slot['end_time']:
                return slot
    return None

# === RENDER CLASS INFO ===
def render_text_display(slot):
    image = Image.new('1', (DISPLAY_WIDTH, DISPLAY_HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    try:
        font_large = ImageFont.truetype(FONT_PATH, 60)
        font_medium = ImageFont.truetype(FONT_PATH, 40)
    except:
        print("⚠ Warning: Falling back to default font")
        font_large = font_medium = ImageFont.load_default()

    y = 20
    # Header
    draw.text((DISPLAY_WIDTH // 2 - 250, y), HEADER_TEXT, font=font_medium, fill=0)
    y += font_medium.getsize(HEADER_TEXT)[1] + 20

    # Class Name
    class_text = f"{slot['class']}"
    draw.text((50, y), class_text, font=font_large, fill=0)
    y += font_large.getsize(class_text)[1] + 10

    # Title (NEW)
    title_text = f"Title: {slot['title']}"
    draw.text((50, y), title_text, font=font_medium, fill=0)
    y += font_medium.getsize(title_text)[1] + 10

    # Instructor
    teacher_text = f"Instructor: {slot['teacher']}"
    draw.text((50, y), teacher_text, font=font_medium, fill=0)
    y += font_medium.getsize(teacher_text)[1] + 10

    # Time
    time_text = f"Time: {slot['start_time']} - {slot['end_time']}"
    draw.text((50, y), time_text, font=font_medium, fill=0)

    return image

# === RENDER EVENT IMAGE ===
def render_event_image(image_path):
    img = Image.open(image_path).convert('1')
    img = ImageOps.fit(img, (DISPLAY_WIDTH, DISPLAY_HEIGHT), Image.LANCZOS)
    return img

# === MAIN LOOP ===
def main():
    epd = epd7in5_V2.EPD()
    epd.init()
    epd.Clear()

    room_id = load_room_id()
    if not room_id:
        print("❌ No room ID found, aborting.")
        return

    event_images = sorted([os.path.join(EVENT_FOLDER, f) for f in os.listdir(EVENT_FOLDER) if f.endswith('.png')])
    event_index = 0

    while True:
        schedule = load_schedule(room_id)
        current_slot = get_current_class(schedule)

        if current_slot:
            print(f"✅ Displaying class: {current_slot['class']}")
            image = render_text_display(current_slot)
        else:
            if event_images:
                event_path = event_images[event_index % len(event_images)]
                print(f"🖼️ Displaying event image: {event_path}")
                image = render_event_image(event_path)
                event_index += 1
            else:
                print("⚠ No events found, displaying fallback message")
                image = Image.new('1', (DISPLAY_WIDTH, DISPLAY_HEIGHT), 255)
                draw = ImageDraw.Draw(image)
                fallback_font = ImageFont.truetype(FONT_PATH, 40)
                draw.text((50, DISPLAY_HEIGHT // 2), "No classes or events right now", font=fallback_font, fill=0)

        epd.display(epd.getbuffer(image))
        time.sleep(900)  # refresh every 15 minutes

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("⚠ Interrupted, clearing display...")
        epd7in5_V2.EPD().init()
        epd7in5_V2.EPD().Clear()
        epd7in5_V2.EPD().sleep()
