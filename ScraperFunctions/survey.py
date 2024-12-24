# To delete all instances of chromedriver for cleaning is: taskkill /F /IM chromedriver.exe /T
#Standard Imports
import logging
from datetime import datetime
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
#Pythonic Data Proccessing Imports
import pandas as pd
import numpy as np
#Webscraper selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException,ElementNotInteractableException
#Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', mode='a'),
        logging.StreamHandler()
    ]
)
# Define a constant for the date format
DATE_FORMAT = "%m/%d/%Y"
# Get today's date
today = datetime.today()
# Format the date using the constant
formatted_date = today.strftime(DATE_FORMAT)


def not_containing(l, filterchar):
    """Return the list filtered to not contain character filterchar

    Args:
        l (list): list to filter
        filterchar (_type_): character to filter out of the list

    Returns:
        []: Filtered array to not include filter char
    """
    return list(filter(lambda text: text != filterchar,l))
def unique(seq):
    """Get the unique values from a list <seq>

    Args:
        seq (list)
    Returns:
        list: unique values in seq
    """
    #Helper that gets all unique values without modifying order. Used with getLinks
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]
def dollar_to_int(dollar_str):
    """Clean dollar strings on apartment listings, replacing with numbers"""
    # Remove the dollar sign, extraneous characters and commas
    clean_str = dollar_str.replace('$', '').replace(',', '').replace("/Person",'')
    # Convert the cleaned string to an integer
    try:
        return int(clean_str)
    except ValueError:
        return None

class MarketSurvey():
    """
    Market Survey class used to search available listings
    on apartments.com in a given area
    """
    def __init__(self,headless = True,verbose = False,ncomps=5):
        service =  Service(executable_path=r".\chromedriver.exe")
        if not headless:
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
        logging.info(f"Beginning survey for {area}...")
        #Open base apartments.com
        self.driver.get("https://www.apartments.com/")
        #Wait until page loads
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "quickSearchLookup"))
        )
        #Enter words into search area
        area_input = self.driver.find_element(By.ID,"quickSearchLookup")
        area_input.send_keys(area)
        
        time.sleep(2)
        #Click button to submit requiest
        button = self.driver.find_element(
            By.CSS_SELECTOR, "button[title='Search apartments for rent']"
        )
        button.click()
        #Wait unitl new page is opened
        try:
            WebDriverWait(self.driver,20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.property-link")))
        except TimeoutException:
            logging.warning("Finding this area took too long (>20 seconds)")
    def filterArea(self,min_price = None,max_price = None):
        """Filter the active Area search page to look for apartments
        between <min_price> and <max_price>

        Args:
            min_price (number, optional): Minimum apt price. Defaults to None.
            max_price (number, optional): Maximum apt price. Defaults to None.
        """
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
        """Get all competitive properties in the area, given the driver is open on the area"""
        links = self.driver.find_elements(By.CSS_SELECTOR, "a.property-link")
        hrefs = [link.get_attribute("href") for link in links]
        self.current_links = hrefs 
    def quit(self):
        self.driver.quit()
    def clean_df(self):
        no_index = self.df.set_index("ID", inplace=False)

        for i in no_index.columns:
            no_index.loc[no_index[i].apply(lambda i: True if re.search('^\\s*$', str(i)) else False), i] = None #Replace whitespace characters with None values for all columns in the dataframe

        no_index = no_index[no_index["Pricing"] != "Call for Rent"]
        #no_index = no_index[no_index["Pricing"].str[0] == "$"] #Only gets pricing rows that have price values, indicated with dollar signs in Apartments.com
        # Security Deposit - Remove extraneous text and attempt convert to float
        deposit = no_index["Security Deposit"]
        numified_sd = pd.to_numeric(
            deposit.apply(
                lambda x:x.partition(" deposit")[0][1:].replace(",", "") if isinstance(x,str) else x
            ),
            errors='coerce'
        )
        no_index["Security Deposit"] = numified_sd

        # Listed Rent  - Remove comma separators, then convert to float
        rents = no_index["Pricing"]
        new_rents = []
        for rent in rents:
            if isinstance(rent,str):
                new_str = rent.replace(",","").replace("$","").replace("/Person","").replace("–", "-").strip()
                if "-" in rent:
                    min, max = rent.split('-')
                    new_rents.append((int(min) + int(max))/2)
                else:
                    new_rents.append(int(new_str))
            else:
                new_rents.append(rent)
        
        no_index["Pricing"] = new_rents
        no_index["Pricing"] = pd.to_numeric(no_index["Pricing"],errors="coerce")

        # Square feet - Remove comma separators, then convert to int
        updated_sqft = []
        for sqft in no_index["Sqft"]:
            sqft = sqft.replace(",","").replace("–", "-")
            if "-" in sqft:
                min,max = sqft.split("-")
                updated_sqft.append((int(min) + int(max))/2)
            else:
                updated_sqft.append(int(sqft))
        no_index["Sqft"] = updated_sqft
        no_index["Sqft"] = no_index["Sqft"].astype(int)

        # Bed/Baths concatenation and formatting
        no_index["Bed/Baths"] = no_index["Beds"].astype(str) + " Bed " + no_index["Baths"].apply(
            lambda x: int(x) if pd.notnull(x) and isinstance(x, (int, float)) and x % 1 == 0 else x).astype(str) + " Bath"
        
        self.df = no_index
    def findIndividualUnits(self,rt_prop,competitor):
        show_more_buttons = self.driver.find_elements(By.CSS_SELECTOR,"button.js-priceGridShowMoreLabel")
        #Click all of the show more buttons
        for button in show_more_buttons:
            try:
                button.click()
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.unitContainer.js-unitContainerV3"))
                )
            except ElementNotInteractableException:
                continue
        
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.unitContainer.js-unitContainerV3"))
        )
        properties = []
        units = self.driver.find_elements(By.CSS_SELECTOR, "li.unitContainer.js-unitContainerV3")

        #Get the depsoit information for each model type and store in a dictionary
        divs = self.driver.find_elements(By.CSS_SELECTOR,'div.priceBedRangeInfo')
        modeldict = {}
        for div in divs:
            model_name = div.find_element(By.CSS_SELECTOR,"span.modelName").text
            
            #If no model name, this is an empty unit - break
            if model_name == "":
                break
            span = div.find_element(By.CSS_SELECTOR,"span.detailsLabel").get_attribute("textContent")
            if "Deposit" in span:
                txt = span.partition("Deposit")[0].strip()
                deposit = txt.split(" ")[-1]
            else:
                deposit = ""
            modeldict[model_name] = deposit
        cols = ["pricing","sqft","available","unit"]
        
        for item in units:
            data_model = item.get_attribute("data-model")
            if data_model in modeldict:
                attributes = {
                    "ID":competitor + " " + data_model,
                    "Area": rt_prop,
                    "Competitor":competitor,
                    "Beds": item.get_attribute("data-beds"),
                    "Baths": item.get_attribute("data-baths"),
                    "Model": data_model,
                    "Security Deposit": modeldict[data_model],
                    "Report Date": datetime.today().strftime(DATE_FORMAT),
                    "Type":"Grid"
                }
                for col in cols:
                    nicercol = col[0].upper() + col[1:]
                    #Unavailable units trip this up, so break if we find one
                    try:
                        attributes[nicercol] = item.find_element(By.CSS_SELECTOR,f"div.{col}Column.column").text.split("\n")[1]
                    except IndexError:
                        #If no data - empty unit, break
                        return properties
                properties.append(attributes)
        return properties
    def findUnitTypes(self,rt_prop,competitor, units):
        properties = []
        for unit in units:
            data_model = unit.find_element(By.CSS_SELECTOR,"span.modelName").text
            available = unit.find_element(By.CSS_SELECTOR,"span.availabilityInfo").text
            
            details = unit.find_element(By.CSS_SELECTOR,'span.detailsTextWrapper')
            arr = details.get_attribute("innerText").split('\n')
            beds,baths,sqft = arr[0],arr[1],arr[2]
            
            if beds == "Studio":
                beds = "0 "
            beds = beds.partition(" ")[0]
            baths = baths.partition(" ")[0]
            sqft = sqft.replace(",","").replace("Sq Ft","")
            
            price_rng = unit.find_element(By.CSS_SELECTOR,"span.rentLabel").text
            price_rng = price_rng.replace("/Person","").strip() #Weird corner case for student listings
            if data_model == "": #Signifies that we have left the valid part of the array
                break
            if "–" in price_rng:
                minimum, maximum = price_rng.split(" – ")
                minimum, maximum = dollar_to_int(minimum), dollar_to_int(maximum)
                if minimum != None and maximum != None:
                    price_rng = (minimum + maximum)/2
                else:
                    price_rng = None
            else:
                price_rng = dollar_to_int(price_rng)
            
            attributes = {
                    "ID":competitor + " " + data_model,
                    "Area": rt_prop,
                    "Competitor":competitor,
                    "Beds": beds,
                    "Baths": baths,
                    "Model": data_model,
                    "Security Deposit": "",
                    "Report Date":formatted_date,
                    "Type": "Gridless",
                    "Pricing": price_rng,
                    "Sqft": sqft,
                    "Available": available,
                    "Unit": data_model
                }
            properties.append(attributes)
        return properties
    def getCompData(self, property):
        properties = []
        #Iterate over all links
        #Wait until page loads
        
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.pricingGridItem.multiFamily")))
        except TimeoutException:
            return      
        #Find details
        prop = self.driver.find_element(By.CSS_SELECTOR,"h1.propertyName").text

        with_unit_key = self.driver.find_elements(By.CSS_SELECTOR,"div.pricingGridItem.multiFamily.hasUnitGrid")
        without_unit_key = self.driver.find_elements(By.CSS_SELECTOR,"div.pricingGridItem.multiFamily")

        if self.verbose:
            logging.info(f"Gathering data for {prop}...")
        
        if len(with_unit_key) > 0:
            properties = self.findIndividualUnits(property,prop)
        elif len(without_unit_key) > 0:
            if self.verbose:
                logging.info("Found gridless item")
            properties = self.findUnitTypes(property,prop,without_unit_key)
        
        address_elem = self.driver.find_element(By.CSS_SELECTOR,'div.propertyAddressContainer')
        address = address_elem.text.partition('\n')[0]
        link = self.driver.current_url
        for model in properties:
            model['Address'] = address
            model['URL'] = link
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
            logging.info(f"Found links: {hrefs}...")

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
        # Drop unnecessary columns
        df_excluded = self.df.drop(columns=["Beds", "Baths"])
        
        # Initialize list to collect results
        result_data = []

        # Iterate over each group and calculate mean and count
        grouped = df_excluded.groupby(['Area', 'Competitor', 'Bed/Baths', 'Report Date'])
        for group_keys, group_df in grouped:
            # Calculate the mean for numeric columns
            mean_values = group_df.mean(numeric_only=True).round(2)
            
            # Check if any row has 'Type' == 'Grid' in the group
            if (group_df['Type'] == 'Grid').any():
                available_units_count = (group_df['Type'] == 'Grid').sum()
            else:
                available_units_count = None  # Assign pd.NA if no 'Grid' rows exist
            
            # Create a dictionary for the row data
            row_data = {
                'Area': group_keys[0],
                'Competitor': group_keys[1],
                'Bed/Baths': group_keys[2],
                'Report Date': group_keys[3],
                'Available_Units_Count': available_units_count,
                **mean_values.to_dict()
            }
            
            # Append the row data to the results list
            result_data.append(row_data)
        
        # Convert the list of dictionaries to a DataFrame
        merged_df = pd.DataFrame(result_data)
        
        #Reindex 
        
        col_list = list(merged_df)
        #Move Available unit count to the end
        col_list.append(col_list.pop(4))
        reindexed = merged_df.reindex(col_list,axis=1)
        
        self.df = reindexed
    def full_survey(self,input_path,rollup = True):
        input_df = pd.read_csv(input_path)
        total_props = len(input_df)
        #Get the dynamic competitor data for each area in the input dataframe
        for index,row in input_df.iterrows():
            self.getAreaData(row["Area"],row["Property Name"],row["Min Price"],row["Max Price"])
            if self.verbose == True:
                logging.info(f"Market Survey complete for {row['Area']}. Survey {np.round((index + 1)/total_props,4) * 100}% complete")
        #Update dataframe with self-contained data
        self.df = pd.DataFrame(self.data)
        #Close webdriver
        self.quit()
        #Clean DataFrame (String to number correction with error coersion)
        self.clean_df()
        #Condense data if asked
        if rollup:
            self.rollup_df()
    def survey_from_links(self,input_path):
        input_df = pd.read_csv(input_path)
        for _, row in input_df.iterrows():
            prop = row['Property']
            link = row['Link']
            if link != "":
                self.driver.get(link)
                data = self.getCompData(prop)
                if data != None:
                    self.data.extend(data)
        self.df = pd.DataFrame(self.data)
        self.quit()
    def modify_df(self,rollup = True):
        self.clean_df()
        if rollup:
            self.rollup_df()
    def to_csv(self,mode,file_path):
        if mode == 'overwrite':
            write_mode = 'w'  # Overwrite mode
            header = True     # Include the header when overwriting
        elif mode == 'append':
            write_mode = 'a'  # Append mode
            header = not pd.io.common.file_exists(file_path)  # Only include header if file doesn't exist
        else:
            raise ValueError("Mode must be 'overwrite' or 'append'")
        #Reset index applied to ensure pivot columns included in output
        self.df.reset_index().to_csv(file_path, mode=write_mode, header=header, index=False)
        logging.info(f"Data saved to {file_path}")
    def to_excel(self, mode, file_path,sheetname):
        if mode not in ['overwrite', 'append']:
            raise ValueError("Mode must be 'overwrite' or 'append'")
        
        if mode == 'overwrite':
            # Overwrite the file by writing the DataFrame to a new Excel file
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
                self.df.to_excel(writer, index=False, sheet_name=sheetname)
        elif mode == 'append':
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                # Append the new DataFrame to the existing sheet
                self.df.to_excel(writer, sheet_name=sheetname,index=True, startrow=writer.sheets[sheetname].max_row,header = False)
        logging.info(f"Data saved to {file_path}")

class MarketSurveyParallel(MarketSurvey):
    @staticmethod
    def process_area_data(row, ncomps, headless=True, verbose=False):
        """Helper method for parallel execution of area data scraping"""
        #Create a nested Market Survey Object (inits a new driver)
        survey = MarketSurvey(headless=headless, verbose=verbose, ncomps=ncomps)
        survey.getAreaData(row["Area"], row["Property Name"], row.get("Min Price"), row.get("Max Price"))
        survey.quit()  # Close the webdriver for this instance
        return survey.data  # Return the scraped data

    def full_survey_parallel(self, input_path, rollup=True, max_workers=4):
        #Parallel Version of Market Survey, opens multiple windows
        input_df = pd.read_csv(input_path)
        all_data = []
        #Oppen parallel processors for each market survey
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    MarketSurveyParallel.process_area_data,
                    row,
                    self.ncomps,
                    self.verbose
                ) for _, row in input_df.iterrows()
            ]

            for future in as_completed(futures):
                try:
                    data = future.result()
                    all_data.extend(data)  # Collect data from each future
                except Exception as e:
                    logging.errror(f"Error encountered: {e}")

        # Combine all collected data into the main DataFrame
        self.df = pd.DataFrame(all_data)
        self.clean_df()  # Clean data if necessary
        if rollup:
            self.rollup_df()

    def to_csv(self, mode, file_path):
        super().to_csv(mode, file_path)
    def to_excel(self,mode,file_path,sheetname):
        super().to_excel(mode,file_path,sheetname)