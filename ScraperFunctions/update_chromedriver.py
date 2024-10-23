#Imports for automatic chromedriver update
from bs4 import BeautifulSoup
import requests
from io import StringIO
import zipfile
import os
import pandas as pd 

def get_update_url(platform):
    #Find the most recent chromedriver download link from https://googlechromelabs.github.io/chrome-for-testing/#stable
    targ = ['linux64','mac-arm64','mac-x64','win32','win64']
    if platform not in targ:
        raise ValueError(f"Platform must be a download type in: {targ}")
    #Use requests module and bs4 to to parse html without a chromedriver
    url = 'https://googlechromelabs.github.io/chrome-for-testing/#stable'
    page = requests.get(url)
    content = page.content
    soup = BeautifulSoup(content, "html.parser")
    tables = soup.find_all('table')
    df = pd.read_html(StringIO(str(tables)))[1]
    #Filter the website's table to get chromedriver for the input platform (will always be one row)
    df = df[(df["Binary"] == "chromedriver") & (df["Platform"] == platform)]
    #Get the URL element from this table
    return df.iloc[0]["URL"]
def download_zip_file(platform):
    #Downloads the most recent zip file of the chromedriver for the input platform
    url = get_update_url(platform)
    with requests.get(url,stream = True) as r:
        r.raise_for_status()
        #Download the zip file in chunks
        with open(r".\chromedriver.zip", 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
def extract_specific_file(zip_file_path, platform, extract_to='.'):
    #Unzip the downloaded file and move the chromedriver to extract_to
    
    # Open the zip file in read mode
    to_extract = f'chromedriver-{platform}/chromedriver.exe'
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        # Get the list of files in the zip
        zip_contents = zip_ref.namelist()
        print(zip_contents)
        
        # Check if the specific file is in the zip file
        if to_extract in zip_contents:
            # Extract the specific file to the desired location
            with zip_ref.open(to_extract) as source, open(os.path.join(extract_to, 'chromedriver.exe'), 'wb') as target:
                target.write(source.read())
            print(f"Extracted 'chromedriver.exe' to: {os.path.abspath(os.path.join(extract_to, 'chromedriver.exe'))}")
        else:
            print(f"File 'chromedriver.exe' not found in the zip archive.")
def update_driver(platform):
    download_zip_file(platform)
    extract_specific_file(r".\chromedriver.zip",platform)
    os.remove(r".\chromedriver.zip")