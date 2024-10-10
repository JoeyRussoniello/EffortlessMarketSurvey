# %%
#To delete all instances of chromedriver for cleaning is: taskkill /F /IM chromedriver.exe /T

#Imports
import time
import re
from datetime import datetime
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException



# Get today's date
today = datetime.today()
# Format the date as YYYY MM DD
formatted_date = today.strftime("%m/%d/%Y")

# %%
#Custom Scraper functions
def not_containing(l, filterchar):
    return list(filter(lambda text: text != filterchar,l))
def get_comps():
    comps = pd.read_csv(r"C:\Users\JosephRussoniello\OneDrive - Red Tail Residential\Python\Apartment Scrape Python Project\.venv\Inputs\Property Comps.csv")
    areas = {}
    for (index, row) in comps.iterrows():
        areas[row["Address"]] = row["Property"]
    return areas
def initializeDriver(headless=True):
    """_summary_

    Args:
        headless (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """    
    #Opens a new chrome driver in headless mode, or regularly
    service =  Service(executable_path=r"C:\Users\JosephRussoniello\OneDrive - Red Tail Residential\Python\Apartment Scrape Python Project\.venv\chromedriver.exe")
    if headless == False:
        driver = webdriver.Chrome(service=service)
    else:
        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
        driver = webdriver.Chrome(service=service,options= options)
    return driver
def findArea(driver,area):
    """Searches an <area> on apartments.com given an active WebDriver"""
    print(f"Beginning survey for {area}...")
    #Open base apartments.com
    driver.get("https://www.apartments.com/")
    #Wait until page loads
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "quickSearchLookup")))

    #Enter words into search area
    area_input = driver.find_element(By.ID,"quickSearchLookup")
    area_input.send_keys(area)
    
    time.sleep(2)
    #Click button to submit requiest
    button = driver.find_element(By.CSS_SELECTOR, "button[title='Search apartments for rent']")
    button.click()

    #Wait until page is found, precautionary measure to future functions
    try:
        WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.property-link")))
    except:
        TimeoutError
def getLinks(driver):
    #Get all competitive properties in the area, given the driver is open on the area
    links = driver.find_elements(By.CSS_SELECTOR, "a.property-link")
    hrefs = [link.get_attribute("href") for link in links]
    return hrefs
def unique(seq):
    #Helper that gets all unique values without modifying order. Used with getLinks
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
def getCompData(driver, rtprop,verbose = False):
    properties = []
    #Iterate over all links
    #Wait until page loads
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.propertyName")))
    except TimeoutError:
        return
    
    #Find details
    prop = driver.find_element(By.CSS_SELECTOR,"h1.propertyName").text
    if verbose == True:
        print(f"Gathering data for {prop}...")
    
    prop_info = driver.find_elements(By.CSS_SELECTOR, "li.unitContainer.js-unitContainer")

    divs = driver.find_elements(By.CSS_SELECTOR,"div.priceBedRangeInfo")

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
#"""
    for item in prop_info:
        data_model = item.get_attribute("data-model")
        if data_model in modeldict:
            attributes = {
                "ID":prop + " " + data_model,
                "Area":rtprop,
                "Property":prop,
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
                    if (properties == None or properties == []) and verbose == True:
                        print("     No data found")
                    return properties
            properties.append(attributes)
    if (properties == None or properties == []) and verbose == True:
        print("     No data found")
    return properties
def getAreaData(driver, area, rt_prop,ncomps = 5,verbose = False):
    #Search for the area on apartments.com
    findArea(driver,area)
    #Get the links for the comps in the area
    hrefs = getLinks(driver)
    #Make sure link list is unique
    hrefs = unique(hrefs)
    if verbose == True:
        print(f"Found links: {hrefs}...")

    properties = []
    numfound = 0
    #Get as many links as possible with data, up to ncomps
    for href in hrefs:
        if numfound == ncomps:
            break
        hrefproperties = getCompData(driver,href,area,rt_prop,verbose)
        if hrefproperties != None and hrefproperties != []:
            properties.extend(hrefproperties)
            numfound += 1
    return properties

def newMarketSurvey(areas_dict,headless=False,verbose=True):
    driver = initializeDriver(headless=headless)
    data = []
    for address,rtprop in areas_dict.items():
        findArea(driver,address)
        try:
            properties = getCompData(driver=driver,rtprop=rtprop,verbose=verbose)
            data.extend(properties)
        except TimeoutException:
            if verbose == True:
                print(f"Invalid prop {address}")
            pass
    driver.quit()
    df = pd.DataFrame(data)
    return df
def clean_df(df):
    #df.set_index("ID",inplace=True)
    for col in df.columns:
        df.loc[df[col].apply(lambda x: bool(re.search(r'^\s*$', str(x)))), col] = None
    df = df[df["Pricing"].str[0] == "$"]
    #Security Deposit
    deposit = df["Security Deposit"]
    numified_sd = deposit.apply(lambda x: pd.to_numeric(x.partition(" deposit")[0][1:].replace(",", ""), errors='coerce') if isinstance(x, str) and " deposit" in x else np.nan).astype(float)
    df["Security Deposit"] = numified_sd

    #Listed Rent 
    rents = df["Pricing"]
    numified_rent = rents.apply(lambda x: x[1:].replace(",","")).astype(float)
    df["Pricing"] = numified_rent

    #Square feet
    df["Sqft"] = df["Sqft"].apply(lambda x: x.replace(",","")).astype(int)
    #Sorry future me, this function is really gross, but just concatenates and shortens the Beds/Baths columns
    df["Bed/Baths"] = df["Beds"].astype(str) + " Bed " + df["Baths"].apply(lambda x: int(x) if pd.notnull(x) and isinstance(x, (int, float)) and x % 1 == 0 else x).astype(str) + " Bath"
    return df
def group_df(df):
    df_excluded = df.drop(columns = ["Beds","Baths"])
    grouped = df_excluded.groupby(['Area','Property','Bed/Baths','Report Date']).mean(numeric_only=True).round(2)
    counts = df_excluded.groupby(['Area','Property','Bed/Baths','Report Date']).size().to_frame(name = 'Units Available')
    grouped = grouped.join(counts)
    return grouped
def write_df(df,path,mode):
    if mode == "a":
        df.to_csv(path,mode=mode,header=False)
    else:
        df.to_csv(path)

# %%
areas = get_comps()
df = newMarketSurvey(areas,headless=True,verbose=True)
cleaned = clean_df(df)
grouped = group_df(cleaned)

# %%
path = r'C:\Users\JosephRussoniello\OneDrive - Red Tail Residential\Python\Apartment Scrape Python Project\.venv\Outputs\Market Survey Data.csv'
write_df(grouped,path = path,mode='a')
