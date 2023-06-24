import os
import random
from datetime import datetime, timedelta
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import yaml
from types import SimpleNamespace



def get_default_chrome_options():
    """ Set arguments for chrome """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument("--user-data-dir=/tmp/chrome-user-data")
    options.add_argument("--remote-debugging-port=9222")
    # Chrome binary path based on local testing or deployment on AWS
    # (i.e. Dockerfile install in opt directory for Docker image)
    if 'home' in os.getcwd():
        # Downloaded from here: https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64
        # %2F920005%2Fchrome-linux.zip?alt=media
        binary_location = './chrome-linux/chrome'  # Local syntax for development
    else:
        # Refer to Dockerfile to see this being installed in Docker Image
        binary_location = '/opt/chrome/chrome'
    options.binary_location = binary_location
    return options


class EarthCamImg:
    """ Class to obtain images from EarthCam """

    def __init__(self, save_dir):
        self.location = 'Columbus Circle'
        self.url = 'https://www.earthcam.com/usa/newyork/columbuscircle/?cam=columbus_circle'
        self.save_dir = save_dir

    def __get_soup(self):
        # Chromedriver path based on local testing or deployment on AWS
        # (i.e. Dockerfile install in opt directory for Docker image)
        if 'home' in os.getcwd():
            # Downloaded from here: https://chromedriver.storage.googleapis.com/95.0.4638.69/chromedriver_linux64.zip
            exe_path = './chromedriver'  # Local syntax for development
        else:
            # Refer to Dockerfile to see this being installed in Docker Image
            exe_path = "/opt/chromedriver"
        browser = webdriver.Chrome(executable_path=exe_path, options=get_default_chrome_options())
        browser.get(self.url)
        html = browser.page_source
        browser.close()
        soup = BeautifulSoup(html, 'html.parser')
        return soup

    def get_imgs_store_on_disk(self):
        soup = self.__get_soup()
        images = soup.findAll("div", attrs={"class": "pic"})
        for image in images:
            jpg_source = image.find("a")["href"]
            jpg_timestamp = image.text

            # Returns a datetime object containing the local date and time
            current_datetime = datetime.now()

            # Store images to disk but do not store images from the current day
            if ('Yesterday'.lower() in jpg_timestamp.lower()) or ('days' in jpg_timestamp):
                if 'Yesterday'.lower() in jpg_timestamp.lower():
                    jpg_datetime = current_datetime - timedelta(days=1)

                if 'days' in jpg_timestamp:
                    for i in jpg_timestamp.split(' '):
                        if i.isnumeric():
                            days = int(i)
                    jpg_datetime = current_datetime - timedelta(days=days)

                # Create File Name for Image
                img_name = jpg_source.split('/')[-1]
                date_time = jpg_datetime.strftime('%d-%b-%Y (%H:%M:%S.%f)')
                jpg_save_name = f'{date_time}__{img_name}'

                # save images
                img_data = requests.get(jpg_source).content
                print(f'Does Directory Exist: {self.save_dir} - {os.path.exists(self.save_dir)}')
                with open(self.save_dir + jpg_save_name, 'wb') as handler:
                    handler.write(img_data)
                    handler.close()
                    print(f'Img Saved: {os.path.join(self.save_dir, jpg_save_name)}')
        return
