#!/usr/bin/python
import argparse
import sys
import time
import json
import os.path
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

parse = argparse.ArgumentParser()
parse.add_argument("-n", "--name", required=True, type=str)
parse.add_argument("-f", "--file", required=True, type=str)
parse.add_argument("-t", "--thumbnail", required=True, type=str)
parse.add_argument("-e", "--email", required=True, type=str)
parse.add_argument("-p", "--password", required=True, type=str)
parse.add_argument("-v", "--visibly_advice", required=True, type=str)
args = parse.parse_args()

file_backup_folder = os.path.dirname(args.file) + "/finished_transfer_movies/" + os.path.basename(args.file)

class TestBitchuteUploadClass(object):
  def __init__(self, name, file, thumb, email, password, visibly_advice):
    self.name = name
    self.file = file
    self.thumb = thumb
    self.email = email
    self.password = password
    self.visibly_advice = visibly_advice

  def setup_method(self, method):

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,720")
    chrome_options.add_argument("--remote-debugging-port=9222")

    # Chrome 115+ includes its own driver, use "chromium" endpoint
    self.driver = webdriver.Chrome(options=chrome_options)

    self.vars = {}
  
  def teardown_method(self, method):
    try:
      self.driver.quit()
    except:
      pass
  
  def test_bitchuteUploadClass(self):

     # Connect to BitChute homepage
     while True:
        try:
           self.driver.get("https://www.bitchute.com/")
           print("Connected to bitchute.com")
           print("Uploading video:", self.name)
        except Exception as e:
           print("Network failure:", e)
           time.sleep(3)
           continue
        else:
           break

     # LOGIN
     while True:
        try:
           WebDriverWait(self.driver, 30).until(expected_conditions.element_to_be_clickable((By.LINK_TEXT, "Login")))
           self.driver.find_element(By.LINK_TEXT, "Login").click()

           WebDriverWait(self.driver, 30).until(expected_conditions.visibility_of_element_located((By.ID, "id_username")))
           self.driver.find_element(By.ID, "id_username").send_keys(self.email)
           self.driver.find_element(By.ID, "id_password").send_keys(self.password)
           self.driver.find_element(By.ID, "auth_submit").click()

           WebDriverWait(self.driver, 30).until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, ".fa-upload > path")))
        except Exception as e:
           print("Login retrying…")
           time.sleep(1)
           continue
        else:
           break

     # Upload page
     while True:
        try:
           self.driver.find_element(By.CSS_SELECTOR, ".fa-upload > path").click()
           WebDriverWait(self.driver, 30).until(expected_conditions.visibility_of_element_located((By.ID, "publish")))
        except:
           print("Upload page retry…")
           continue
        else:
           break

     # Fill in title + sensitivity
     while True:
        try:
          self.driver.find_element(By.ID, "title").send_keys(self.name)
          self.driver.find_element(By.XPATH, f"//option[@value='{self.visibly_advice}']").click()
        except:
          continue
        else:
          break

     # Upload THUMBNAIL
     while True:
        try:
          WebDriverWait(self.driver, 30).until(expected_conditions.presence_of_element_located((By.NAME, "thumbnailInput")))
          self.driver.find_element(By.NAME, "thumbnailInput").send_keys(self.thumb)
          time.sleep(3)
        except:
          continue
        else:
          break

     # Upload VIDEO
     while True:
        try:
          WebDriverWait(self.driver, 30).until(expected_conditions.presence_of_element_located((By.NAME, "videoInput")))
          self.driver.find_element(By.NAME, "videoInput").send_keys(self.file)
          time.sleep(3)
        except:
          continue
        else:
          break

     # Publish button
     while True:
        try:
           title = self.driver.title
           if title == "Upload":
              print("Clicking Publish…")
              time.sleep(2)
              self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
           else:
              print("Upload complete!")
              break
        except:
           continue

     # Notification page closing
     time.sleep(3)
     try:
        self.driver.find_element(By.CSS_SELECTOR, "#notifylink path").click()
        time.sleep(1)
     except:
        pass

Bitchute = TestBitchuteUploadClass(args.name, args.file, args.thumbnail, args.email, args.password, args.visibly_advice)

Bitchute.setup_method("")

while True:
   try: 
      Bitchute.test_bitchuteUploadClass()
   except Exception as e:
      print("Retry Upload:", e)
      time.sleep(1)
   else:
      print("Move", args.file, "to", file_backup_folder)
      try:
         shutil.move(args.file, file_backup_folder)
      except:
         pass
      break

Bitchute.teardown_method("")
