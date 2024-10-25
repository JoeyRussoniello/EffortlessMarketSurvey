# EffortlessMarketSurvey
# Table of Contents
1. [Project Description](#project-description)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Configuration](#configuration)
   1. [Default Configuration](#default-configuration)
6. [Usage](#usage)
7. [Output](#output)
    1. [Basic Market Summary](#1-basic-market-summary-no-internal-data-rolled-up)
    2. [Market Comparison](#2-market-comparison-with-internal-data-rolled-up)
8. [Future Improvements](#future-improvements)
## Project Description
EffortlessMarketSurvey is a robust real estate web scraper designed to automate market surveys, making competitor analysis easy and efficient. With seamless data collection from apartments.com and built-in Power BI dashboard templates, you can focus on strategic insights without worrying about manual data collection.

## Features
- **Parallel Data Processing**: Run multiple property surveys simultaneously, significantly reducing total runtime for large inputs.
- **Automatic Chromedriver Updates**: Ensures your scraper runs smoothly by always fetching the latest chromedriver.
- **Dynamic Competitor Fetching**: Customize the competitor search for relevancy on apartments.com.
- **Customizable Data Collection**: Tailor the scraper to return only the data you need, with options to specify the number of properties.
- **Data Formatting**: Choose between rolled-up competitor descriptions for high-level overviews or detailed unit availability for deeper insights.

## Requirements 
The following dependencies must be installed to run the project:

    - beautifulsoup4==4.12.0
    - requests==2.31.0
    - pandas==2.1.1
    - selenium==4.14.0
    - numpy==1.26.0
    
You can install the required packages by running:

``` bash
pip install -r requirements.txt
```

## Installation
### Step 1: Prerequisites
Ensure that you have installed:
- [Python](https://www.python.org/downloads/) 3.8 or later
- [pip](https://pip.pypa.io/en/stable/installation/)
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

### Step 2: Clone the repository
1. Clone this repository to your local machine
```bash
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
Customize the scraper by editing the settings in the `config.json` file.

- **platform**: Defines the operating system for installing Chromedriver. Options are:
  - `linux64`, `mac-arm64`, `mac-x64`, `win32`, `win64`
- **headless**: If set to `true`, the browser runs in the background without displaying any windows.
- **verbose**: When set to `true`, detailed logs of the scraper's progress will be printed.
- **ncomps**: Number of competitors to survey for each input property.
- **input_path**: Path to the input CSV file for scraping (default: `Input.csv`).
- **rollup**: When `true`, data will be summarized into a pivot table. When `false`, individual listings are shown.
- **output_path**: Path to the output CSV file (default: `Output.csv`).
- **output_mode**: File writing mode (`overwrite` or `append`).
- **parallel_members**: Amount of parallel instances to open at once (default: `4`). Set to 0 for no parallelism.

### Default Configuration
```json
{
    "platform": "win64",    // Choose your platform here - windows 64 by default
    "headless": true,       // Run browser in headless mode
    "verbose": true,        // Print detailed log information
    "ncomps": 5,            // Survey 5 competitors for each area
    "input_path": "Input.csv",   // Input file path
    "rollup": true,             // Roll-up summary to preserve space
    "output_path": "Output.csv", // Output file path
    "output_mode": "append" ,    // Append to existing output instead of overwriting
    "parallel_members": 0        // Do not use parallel members for web scraping
}
```
*Warning: Enabling parallelism for scraping multiple properties can significantly increase computational cost and may impact performance, especially on systems with limited resources. Running in parallel requires more CPU and memory, which may lead to high system load or throttling on low-power devices. Adjust parallel_members based on your system capacity to prevent potential slowdowns or crashes.*

## Usage
Set up the `config.json` file with your preferred settings and Operating System

Set up your `Input.csv` file with the following columns (example data included):

| Area          | Property Name     | Min Price | Max Price |
|---------------|-------------------|-----------|-----------|
| New York, NY  | Central Park Apts | 1500      | 3500      |
| Miami, FL     | Oceanview Condos  | 1000      | 3000      |

- **Area**: The area you want to search around on apartments.com
  - *Note: DO NOT ENTER A SPECIFIC ADDRESS. Enter a street or city to return a list of properties*
- **Min Price**: Sets the minimum monthly rent filter parameter in apartments.com. If left blank, it will not filter.
- **Max Price**: Sets the maximum monthly rent filter parameter in apartments.com. If left blank, it will not filter.


Run the scraper by executing the following command in the terminal:
``` bash
python main.py
```

## Dashboards
EffortlessMarketSurvey currently includes two Power BI dashboard templates to help visualize your market survey results:

### 1. Basic Market Summary (No Internal Data, Rolled Up)
This dashboard gives you a high-level overview of competitor properties.

1. Run the scraper with `rollup = true` in `config.json`.
2. Open `Dashboards/Market Survey Template.pbit` in PowerBI desktop.
3. Connect the dashboard to your `Output.csv` file.

### 2. Market Comparison (With Internal Data, Rolled Up)
Compare your property’s performance with the scraped competitor data.

1. Run the scraper with `rollup = true` in `config.json`.
2. Map your portfolio's data into `Examples/PortfolioOutput.csv`.
2. Open `Dashboard/Market Comparison Dashboard.pbit` in PowerBI desktop.
3. Connect the dashboard to both `Output.csv` and `Portfolio_Performance.csv`.

## Future Improvements
- More prebuilt PowerBI Dashboard Templates, and Image examples
    - BI Equivalents for data that hasn't been rolled up
- Fixed Input Option for webscraping (provide a set list of links to peruse and return their values without dynamically fetching properties)
- Further Updates to Large Example Input and Output datasets, and screenshots of their usage in Dashboards
