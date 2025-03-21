import os
import sys
import time
import logging
import random
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# Get command-line arguments
if len(sys.argv) != 3:
    print("Usage: python script.py <date_number> <time_slot>")
    sys.exit(1)

# Extract input values
date_num = sys.argv[1].strip("'\"") 
time_val = sys.argv[2].strip("'\"") 

print(f"Looking for: {date_num} at {time_val}")

# Set the path to your Chrome profile
profile_path_file = r"ADD_YOUR_PATH_HERE\chromeProfilePath.txt"  # <-- Replace with your actual path

if not os.path.exists(profile_path_file):
    print("chromeProfilePath.txt not found. Exiting.")
    sys.exit(1)

with open(profile_path_file, "r") as f:
    profile_path = f.read().strip()

# Set up logging
logging.basicConfig(filename="gym_bot.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Start browser session
def launch_browser():
    opts = webdriver.ChromeOptions()
    opts.add_argument(f"user-data-dir={profile_path}")  # Uses your Chrome profile
    opts.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=opts)
    driver.get("https://applications2.ucy.ac.cy/sportscenter/online_reservations_pck2.insert_reservation?p_lang=")
    return driver

# Function to safely click buttons (to avoid stale elements)
def click_safe(driver, xpath, tries=3):
    for _ in range(tries):
        try:
            el = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            el.click()
            time.sleep(1)
            return True
        except (StaleElementReferenceException, TimeoutException):
            print(f"Retry clicking: {xpath}")
            time.sleep(2)
    print(f"Failed to click: {xpath}")
    return False

# Function to attempt booking
def try_booking(driver):
    print("Trying to book...")
    driver.refresh()
    time.sleep(3)

    # Navigate through the reservation process
    click_safe(driver, "//a[contains(text(),'Κρατήσεις')]")
    click_safe(driver, "//option[contains(text(),'Γυμναστήριο')]")
    click_safe(driver, "//button[contains(text(),'Επόμενο')]")
    click_safe(driver, f"//button[contains(@class, 'btn-primary') and text()='{date_num}']")
    
    # Select time slot
    dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "p_sttime")))
    dropdown.click()
    time.sleep(1)
    click_safe(driver, f"//select[@name='p_sttime']/option[text()='{time_val}']")

    # Enter purpose (random two characters)
    purpose_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "p_skopos")))
    purpose_box.send_keys("TESTO")

    # Confirm booking
    click_safe(driver, "//button[contains(text(),'Καταχώρηση')]")
    click_safe(driver, "//button[contains(text(),'Καταχώρηση')]")

    # Check if reservation was successful
    time.sleep(3)
    if driver.find_elements(By.CLASS_NAME, "text-danger"):
        print(f"Reservation failed. Retrying in {DELAY} seconds...")
        return False
    else:
        print(" Reservation Successful!")
        logging.info(f"Reservation made for {date_num} at {time_val}.")
        return True


while True:
    try:
        if try_booking(driver):
            break
        print(f"No available spots. Retrying in {DELAY} seconds...")
        time.sleep(DELAY)
    except Exception as e:
        print(f"Error: {e}. Restarting check...")
        time.sleep(DELAY)

# Close browser when done
driver.quit()
print("Reservation process completed.")
