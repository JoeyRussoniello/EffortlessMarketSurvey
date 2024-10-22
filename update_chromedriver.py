#Imports for automatic chromedriver update
from bs4 import BeautifulSoup
import requests
from io import StringIO
import zipfile
import os
import pandas as pd 

def get_update_url(platform):
    targ = ['linux64','mac-arm64','mac-x64','win32','win64']
    if platform not in targ:
        raise ValueError(f"Platform must be a download type in: {targ}")
    url = 'https://googlechromelabs.github.io/chrome-for-testing/#stable'
    page = requests.get(url)
    content = page.content
    soup = BeautifulSoup(content, "html.parser")
    tables = soup.find_all('table')
    df = pd.read_html(StringIO(str(tables)))[1]
    df = df[(df["Binary"] == "chromedriver") & (df["Platform"] == platform)]
    #Get the URL element from this table
    return df.iloc[0]["URL"]
def download_zip_file(platform):
    url = get_update_url(platform)
    with requests.get(url,stream = True) as r:
        r.raise_for_status()
        
        with open(r".\chromedriver.zip", 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
def extract_specific_file(zip_file_path, platform, extract_to='.'):
    # Open the zip file in read mode
    to_extract = f'chromedriver-{platform}/chromedriver.exe'
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        # Get the list of files in the zip
        zip_contents = zip_ref.namelist()
        print(zip_contents)
        # Check if the specific file is in the zip file
        if to_extract in zip_contents:
            # Extract the specific file
            extracted_path = zip_ref.extract(to_extract, extract_to)
            final_destination = os.path.join(extract_to, 'chromedriver.exe')
            os.remove(final_destination)
            os.rename(extracted_path, final_destination)
            print(f"Extracted 'chomedriver.exe' to: {os.path.abspath(extract_to)}")
        else:
            print(f"File 'chromedriver.exe' not found in the zip archive.")
def update_driver(platform):
    download_zip_file(platform)
    extract_specific_file(r".\chromedriver.zip",platform)
    os.remove(r".\chromedriver.zip")