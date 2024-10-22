#To delete all instances of chromedriver for cleaning is: taskkill /F /IM chromedriver.exe /T

#Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd
import numpy as np
from datetime import datetime
import re

# Get today's date
today = datetime.today()
# Format the date as YYYY MM DD
formatted_date = today.strftime("%m/%d/%Y")

def not_containing(l, filterchar):
    return list(filter(lambda text: text != filterchar,l))
def unique(seq):
    #Helper that gets all unique values without modifying order. Used with getLinks
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

class MarketSurvey():
    def __init__(self,headless = True,verbose = False,ncomps=5):
        service =  Service(executable_path=r".\chromedriver.exe")
        if headless == False:
            self.driver = webdriver.Chrome(service=service)
        else:
            options = Options()
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
            self.driver = webdriver.Chrome(service=service,options= options)
        self.verbose = verbose
        self.data = []
        self.current_links = []
        self.used_links = []
        self.ncomps = ncomps
        self.df = None
    def findArea(self,area):
        """Searches an <area> on apartments.com given an active WebDriver"""
        print(f"Beginning survey for {area}...")
        #Open base apartments.com
        self.driver.get("https://www.apartments.com/")
        #Wait until page loads
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "quickSearchLookup")))
        #Enter words into search area
        area_input = self.driver.find_element(By.ID,"quickSearchLookup")
        area_input.send_keys(area)
        
        time.sleep(2)
        #Click button to submit requiest
        button = self.driver.find_element(By.CSS_SELECTOR, "button[title='Search apartments for rent']")
        button.click()
        #Wait unitl new page is opened
        try:
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.property-link")))
        except TimeoutError:
            print("This took too long")
    def filterArea(self,min_price = None,max_price = None):
        filter_button = self.driver.find_element(By.ID, "rentRangeLink")
        filter_button.click()
        time.sleep(0.5)
        if min_price:
            min_area = self.driver.find_element(By.ID,"min-input")
            min_area.send_keys(min_price)
        if max_price:
            max_area = self.driver.find_element(By.ID,"max-input")
            max_area.send_keys(max_price)
        
        button = self.driver.find_element(By.CLASS_NAME, "done-btn")
        button.click()
        time.sleep(0.5)
    def getAreaLinks(self):
    #Get all competitive properties in the area, given the driver is open on the area
        links = self.driver.find_elements(By.CSS_SELECTOR, "a.property-link")
        hrefs = [link.get_attribute("href") for link in links]
        self.current_links = hrefs 
    def quit(self):
        self.driver.quit()
    def clean_df(self):
        self.df.set_index("ID", inplace=True)

        for i in self.df.columns:
            self.df.loc[self.df[i].apply(lambda i: True if re.search('^\\s*$', str(i)) else False), i] = None

        self.df = self.df[self.df["Pricing"].str[0] == "$"]

        # Security Deposit - Remove extraneous text and convert to float
        deposit = self.df["Security Deposit"]
        numified_sd = deposit.apply(lambda x: x.partition(" deposit")[0][1:].replace(",", "") if type(x) == str else x).astype(float)
        self.df["Security Deposit"] = numified_sd

        # Listed Rent 
        rents = self.df["Pricing"]
        numified_rent = rents.apply(lambda x: x[1:].replace(",", "")).astype(float)
        self.df["Pricing"] = numified_rent

        # Square feet
        self.df["Sqft"] = self.df["Sqft"].apply(lambda x: x.replace(",", "")).astype(int)

        # Bed/Baths concatenation and formatting
        self.df["Bed/Baths"] = self.df["Beds"].astype(str) + " Bed " + self.df["Baths"].apply(
            lambda x: int(x) if pd.notnull(x) and isinstance(x, (int, float)) and x % 1 == 0 else x).astype(str) + " Bath"
    def getCompData(self, property):
        properties = []
        #Iterate over all links
        #Wait until page loads
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.propertyName")))
        except TimeoutError:
            return
        
        #Find details
        prop = self.driver.find_element(By.CSS_SELECTOR,"h1.propertyName").text
        if self.verbose == True:
            print(f"Gathering data for {prop}...")
        
        prop_info = self.driver.find_elements(By.CSS_SELECTOR, "li.unitContainer.js-unitContainer")

        divs = self.driver.find_elements(By.CSS_SELECTOR,"div.priceBedRangeInfo")

        #Bro just learned list comprehension
        plans = [div.find_element(By.CSS_SELECTOR, "span.modelName").text for div in divs]
        details = [div.find_element(By.CSS_SELECTOR, "h4.detailsLabel").text for div in divs]


        #Remove extra blank entries
        plans = not_containing(plans,"")
        details = not_containing(details,"")

        #Disgusting list comprehensions to get values from details
        sqft = []
        deposits = []
        for detail in details:
            if "deposit" in detail:
                sqft.append("".join(detail.partition("\n")[0].split(",")[2:]).strip())
                deposits.append(detail.split("\n")[1].partition("deposit")[0] + "deposit")
            elif "sq ft" in detail:
                sqft.append("".join(detail.split(",")[2:]).strip())
                deposits.append("")
            else:
                sqft.append("")
                deposits.append("")

        modeldict = {plans[i]: [sqft[i],deposits[i]] for i in range(len(plans))}

        cols = ["pricing","sqft","available","unit"]
        for item in prop_info:
            data_model = item.get_attribute("data-model")
            if data_model in modeldict:
                attributes = {
                    "ID":prop + " " + data_model,
                    "Area": property,
                    "Competitor":prop,
                    "Beds": item.get_attribute("data-beds"),
                    "Baths": item.get_attribute("data-baths"),
                    "Model": data_model,
                    "Security Deposit": modeldict[data_model][1],
                    "Report Date":formatted_date,
                }
                for col in cols:
                    nicercol = col[0].upper() + col[1:]
                    #Unavailable units trip this up, so break if we find one
                    try:
                        attributes[nicercol] = item.find_element(By.CSS_SELECTOR,f"div.{col}Column.column").text.split("\n")[1]
                    except IndexError:
                        if (properties == None or properties == []) and self.verbose == True:
                            print("     No data found")
                        return properties
                properties.append(attributes)
        if (properties == None or properties == []) and self.verbose == True:
            print("     No data found")
        return properties
    def getAreaData(self, area, property,min_price = None,max_price = None):
        #Search for the area on apartments.com
        self.findArea(area)
        
        #Filter the area
        if min_price or max_price:
            self.filterArea(min_price,max_price)
            time.sleep(2)
        #Get the links for the comps in the area
        self.getAreaLinks()
        #Make sure link list is unique
        hrefs = unique(self.current_links)
        if self.verbose == True:
            print(f"Found links: {hrefs}...")

        numfound = 0
        #Get as many links as possible with data, up to ncomps
        for href in hrefs:
            if numfound == self.ncomps:
                break
            self.driver.get(href)
            hrefproperties = self.getCompData(property)
            if hrefproperties != None and hrefproperties != []:
                self.data.extend(hrefproperties)
                self.used_links.append(href)
                numfound += 1
    def rollup_df(self):
        df_excluded = self.df.drop(columns = ["Beds","Baths"])
        grouped = df_excluded.groupby(['Area','Competitor','Bed/Baths','Report Date']).mean(numeric_only=True).round(2)
        self.df = grouped
    def full_survey(self,input_path,rollup = True):
        input_df = pd.read_csv(input_path)
        for _,row in input_df.iterrows():
            self.getAreaData(row["Area"],row["Property Name"],row["Min Price"],row["Max Price"])
        self.df = pd.DataFrame(self.data)
        self.quit()
        self.clean_df()
        if rollup:
            self.rollup_df()
    def write_output(self,mode,file_path):
        if mode == 'overwrite':
            write_mode = 'w'  # Overwrite mode
            header = True     # Include the header when overwriting
        elif mode == 'append':
            write_mode = 'a'  # Append mode
            header = not pd.io.common.file_exists(file_path)  # Only include header if file doesn't exist
        else:
            raise ValueError("Mode must be 'overwrite' or 'append'")
        
        self.df.reset_index().to_csv(file_path, mode=write_mode, header=header, index=False)