### EffortlessMarketSurvey
## Project Description
This project is a real-estate web scraper designed to extract compset data from apartments.com. It uses requests and Selenium to automate the process of collecting and parsing data for an input area to streamline the Market Survey process and make competitor comparison easy, efficient, and free. The data is saved into Outputs.csv by default, but export paths can be changed in the main.py function.

## Features
- Automatic Chromedriver Updates, usable for all systems where chromedriver is available 
- Dynamic Competitor Fetching/Filtering from an apartments.com search
- Automatic data collection with customizable compset sizes
- Built-in data formatting procedures w/ two options: 
    - Data roll-up condensing apartment.com listings into smaller, competitor descriptions (useful for large portfolios)
    - Individual Unit Availability list (useful for small portfolios to see the niche details)
## Requirements 
The following dependencies must be installed to run the project:
    beautifulsoup4==4.12.0\
    requests==2.31.0\
    pandas==2.1.1\
    selenium==4.14.0\
    numpy==1.26.0\
You can install the required packages by running

``` bash
pip install -r requirements.txt
```

## Installation
1. Clone this repository
``` bash
git clone https://github.com/JoeyRussoniello/EffortlessMarketSurvey
```
2. Navigate to this repository
``` bash
cd EffortlessMarketSurvey
```
3. Install the required python packages
``` bash
pip install -r requirements.txt
```

## Configuration
To configure the scraper, modify the following settings in the config.json file

- **platform**, String: The operating platform used to install the chromedriver. 
    -Must be either ['linux64','mac-arm64','mac-x64','win32','win64']
- **headless**, Boolean: The Visisbility Status of the Opened Browser Window.
- **verbose**, Boolean: When set to true, running main will print more specifics on survey progress and actions.
- **ncomps**, Integer: Number of comps to Survey for each input property.
- **input_path**, String: Path to the input csv file - default 'Input.csv'.
- **rollup**, Boolean: When true rolls up the dataframe into a pivot table, when false leaves each individual apartment listing as its own entry
- **output_path**, String: Path to the output csv file - default 'Output.csv'.
- **output_mode**, String: The Output File Writing mode, "overwrite" completely overwrite the data and "append" will append data onto the existing file at output_path (relies on same headers).
    -Must be either 'overwrite' or 'append'

### Default Configuration
``` json
{
    "platform": "win64",
    "headless": true,
    "verbose": true,
    "ncomps": 5,
    "input_path": "Input.csv",
    "rollup": true,
    "output_path": "Output.csv",
    "output_mode": "append"
}
```

## Usage
Set up your Input.csv file (wherever it is stored) with the following columns. If you are using the Default Input.csv, some example listings are already present
- Area: The Area that you want to search around on apartments.com
    - *Note: DO NOT ENTER A SPECIFIC ADRESS. ENTER A GENERAL AREA SO THAT APARTMENTS.COM WILL RETURN A LIST OF PROPERTIES INSTEAD OF A SINGLE PROPERTY*
- Property Name: The Name you'd like the area to be listed as. Ex: A portfolio's property in that location
- Min Price: Sets minimum monthly rent filter parameter in apartments.com, if left blank will not filter
- Max Price: Sets maximum monthly rent filter parameter in apartments.com, if left blank will not filter

Run the scraper by executing the following command in the terminal:
``` bash
python main.py
```
## Output
Output will be stored in CSV format, in the location of "output_path" found in config.json

## Future Improvements
- Prebuilt PowerBI Dashboard Templates
    - With External Data (Used to compare your property with properties in the area)
        - Useful for Sellers
    - Without External Data (Used to gauge the prices of apartments in area without local comparison)
        - Useful for Buyers
- Fixed Input Scraping Options (provide a set list of links to peruse and return their values without dynamically fetching properties)
- Large Example Input and Output datasets, and screenshots of their usage in Dashboards
