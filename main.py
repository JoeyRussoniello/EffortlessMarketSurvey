from ScraperFunctions.update_chromedriver import update_driver
from ScraperFunctions.survey import MarketSurvey, MarketSurveyParallel
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
PARALLEL = config['parallel_members']

#Update the chrome drivers
update_driver(PLATFORM)
if PARALLEL == 0 or PARALLEL == 1:    
    #Perform Market Survey Without Any Parallelism
    survey = MarketSurvey(headless = HEADLESS, verbose = VERBOSE, ncomps = NCOMPS) #Initialize Market Survey with parameter inputs
    survey.full_survey(input_path = INPUT_PATH,rollup = ROLLUP)
    survey.write_output(mode = OUTPUT_MODE,file_path = OUTPUT_PATH)
else:
    #Perform parallel Market Surveys. More Computationally demanding
    survey = MarketSurveyParallel(headless = HEADLESS,verbose = VERBOSE, ncomps = NCOMPS)
    survey.full_survey_parallel(input_path = INPUT_PATH,rollup = ROLLUP,max_workers=PARALLEL)
    survey.write_output(OUTPUT_MODE,OUTPUT_PATH)