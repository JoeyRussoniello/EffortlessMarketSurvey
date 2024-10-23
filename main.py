from ScraperFunctions.update_chromedriver import update_driver
from ScraperFunctions.survey import MarketSurvey
import json

#Get variables from the config file
with open("config.json", "r") as r:
    config = json.load(r)

PLATFORM = config['platform']
HEADLESS = config['headless']
VERBOSE = config['verbose']
NCOMPS = config['ncomps']
INPUT_PATH = config['input_path']
ROLLUP = config['rollup']
OUTPUT_PATH = config['output_path']
OUTPUT_MODE = config['output_mode']

#Update the chrome drivers
update_driver(PLATFORM)
#Perform market survey on the properties and criteria given in input.csv and config.json
survey = MarketSurvey(headless = HEADLESS, verbose = VERBOSE, ncomps = NCOMPS) #Initialize Market Survey with parameter inputs
survey.full_survey(input_path = INPUT_PATH,rollup = ROLLUP)
survey.write_output(mode = OUTPUT_MODE,file_path = OUTPUT_PATH)