import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
# How often to retry booking (in seconds)
CHECK_INTERVAL=3

# Check if user gave the required arguments (date and time)
if len(sys.argv)!=3:
    print("Usage: python gym_reservation.py <date_number> <time_slot>")
    sys.exit(1)

# Get the date and time slot from the user (e.g., 24 and 09:30)
date_number=sys.argv[1]
time_slot=sys.argv[2]

print("Trying to book for date:",date_number,"at",time_slot)

# Path to your saved Chrome profile
base_dir = os.path.dirname(__file__)
file_path = os.path.join(base_dir, "chromeProfilePath.txt")

# If the file with the profile path doesn’t exist, exit
if not os.path.exists(file_path):
    print("chromeProfilePath.txt not found.")
    sys.exit(1)

# Read the actual path from the file
with open(file_path,"r") as file:
    path=file.read().strip()

# Function to open Chrome using your profile so you're logged in
def start_browser():
    options=webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={path}")
    driver=webdriver.Chrome(options=options)
    driver.get("https://applications2.ucy.ac.cy/sportscenter/online_reservations_pck2.insert_reservation?p_lang=")
    time.sleep(3)
    return driver

# Function that clicks on a button or link using XPath
def click(driver,xpath):
    try:
        element=driver.find_element(By.XPATH,xpath)
        element.click()
        time.sleep(1)  # wait a bit for the action to complete
        return True
    except:
        return False

# Main function that tries to book a reservation
def book(driver):
    print("Trying to reserve...")
    driver.refresh()  # refresh the page
    time.sleep(3)  # wait for page to load

    # Step 1: Navigate to the gym reservation section
    click(driver,"//a[contains(text(),'Κρατήσεις')]")
    click(driver,"//option[contains(text(),'Γυμναστήριο')]")
    click(driver,"//input[@type='checkbox']")
    click(driver,"//button[contains(text(),'Επόμενο')]")

    # Step 2: Click on the correct date
    click(driver,f"//button[text()='{date_number}']")
    time.sleep(1)

    try:
        # Step 3: Open the time dropdown and pick the correct time
        driver.find_element(By.NAME,"p_sttime").click()
        time.sleep(1)
        driver.find_element(By.XPATH,f"//option[text()='{time_slot}']").click()

        # Step 4: Type in a reason (can be anything, here just 'ok')
        driver.find_element(By.NAME,"p_skopos").send_keys("ok")

        # Step 5: Click the first submit button
        click(driver,"//button[contains(text(),'Καταχώρηση')]")

        # Step 6: Confirm by clicking the final submit button
        click(driver,"//button[contains(text(),'Καταχώρηση')]")

        # Step 7: Wait and check if we got a red error message (means failed)
        time.sleep(2)
        if driver.find_elements(By.CLASS_NAME,"text-danger"):
            print("No spot available.")
            return False
        else:
            print("Reservation successful!")
            return True
    except:
        print("Something went wrong during booking.")
        return False

# Start the browser and open the site
driver=start_browser()

# Try to book in a loop until successful
while True:
    if book(driver):
        break
    print("Retrying in",CHECK_INTERVAL,"seconds...")
    time.sleep(CHECK_INTERVAL)

# Close the browser after reservation
driver.quit()
print("Done.")