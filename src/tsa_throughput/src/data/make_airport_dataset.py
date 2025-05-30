import json
from datetime import datetime
from dotenv import find_dotenv, load_dotenv
import logging
import os
import pandas
from pathlib import Path
from argparse import ArgumentParser


def processFile(inputFile, airportCode, outputDir, logger):
    """
    Processes a single file
    """
    logger.info(f'Processing csv file: {inputFile}')
    
    df = processSingleFile(inputFile, airportCode)

    df = postProcessDataframe(df, outputDir, logger)
    df = pivotDataframe(df)

    outputFile = f'{outputDir}/' + getOutputFile(inputFile, airportCode, '.csv')

    logger.info(f'Output file: {outputFile}')
    csv_export = df.to_csv(outputFile, index=False)


def processDir(inputDir, matchString, airportCode, outputDir, logger):
    """
    Processes a group of files in a directory with option matchstring to fileter
    Note: There is also a hard-coded .json filter in the code.
    """
    logger.info(f'Processing all files in: {inputDir}')

    numFilesProcessed = 0

    # Loop through the specified input directory looking for json files
    for entry in sorted(os.scandir(inputDir), key=lambda e: e.name):
        if (entry.path.endswith('.json') and 
            entry.is_file()):

            # If a matchString was specified, let's ensure the entry matches
            if(not matchString or matchString in entry.path):

                if(numFilesProcessed == 0):
                    logger.info(f'Processing: {entry.name}')
                    df = processSingleFile(entry.path, airportCode)
                else:
                    logger.info(f'Processing: {entry.name}')
                    #df = df.append(processSingleFile(entry.path, airportCode), ignore_index=True)
                    df = pandas.concat([df, processSingleFile(entry.path, airportCode)], ignore_index=True)
                
                numFilesProcessed += 1
            else:
                logger.info(f'Skipping file: {entry.path}')

        else:
            logger.info(f'Skipping file: {entry.path}')
   
    logger.info(f'Files Processed: [{numFilesProcessed}].')
        
    # If we processed at least one file, process the dataframe and write out the file
    if (numFilesProcessed > 0):
        df = postProcessDataframe(df, outputDir, logger)
        df = pivotDataframe(df)
        
        # Make a more meaningful filename for All airports.
        if(airportCode is None):
            airportCodeString = 'All'
        else:
            airportCodeString = airportCode

        # Generate outputFile path
        outputFile = f'{outputDir}/TsaThroughput.{airportCodeString}.csv'

        logger.info(f'Output file: {outputFile}')
        csv_export = df.to_csv(outputFile, index=False)
    else:
        logger.info(f'No output file created.')
     

def processCsv(inputFile, airportCode, outputDir, logger):
    """
    Processes a csv file
    """
    logger.info(f'Processing file: {inputFile}')

    fileDf = pandas.read_csv(f'{inputFile}', header='infer')

    # If an airportCode is specfied, let's filter on it
    for code in airportCode.splitlines():
        logger.info(f'Processing: {code}')
        df = fileDf[fileDf['AirportCode'] == code]

        df = pivotDataframe(df)

        outputFile = f'{outputDir}/TsaThroughput.{code}.csv'
        logger.info(f'Output file: {outputFile}')
        csv_export = df.to_csv(outputFile, index=False)

def processSingleFile(file, airportCode):
    
    #load json file
    with open(file) as f:
        data = json.load(f)

    #normalize and store in df
    df = pandas.json_normalize(data,
        record_path=['Airports', 'Days', 'Checkpoints', 'Hours'],
        meta=[
            ['Airports', 'Days', 'Checkpoints', 'CheckpointName'],
            ['Airports', 'Days', 'Date'],
            ['Airports', 'AirportCode'],
            ['Airports', 'AirportName'],
            ['Airports', 'City'],
            ['Airports', 'State'],
        ],
    )
    
    #Convert to datetime and get time
    df['Hour'] = pandas.to_datetime(df['Hour'], errors='coerce')
    df['Hour'] = df['Hour'].dt.time

    #Convert to datetime and get date
    df['Airports.Days.Date'] = pandas.to_datetime(df['Airports.Days.Date'], errors='coerce')
    df['Airports.Days.Date'].dt.date
        
    df = df.rename(columns =
    {
        'Airports.Days.Date' : 'Date', 
        'Airports.AirportCode' : 'AirportCode', 
        'Airports.AirportName' : 'AirportName',
        'Airports.City' : 'City',
        'Airports.Days.Checkpoints.CheckpointName' : 'CheckpointName',
        'Airports.State' : 'State'
    }, 
    inplace=False)

    # If an airportCode is specfied, let's filter on it
    if(airportCode) :
        df = df[df['AirportCode'] == airportCode]

    return df

def postProcessDataframe(df, outputDir, logger):
    df = df[['Date', 'Hour', 'AirportName', 'AirportCode', 'City', 'State', 'CheckpointName', 'Amount']]
    df.sort_values(by=['Date','Hour', 'AirportCode', 'CheckpointName'], inplace=True)
       
    # Generate outputFile path
    outputFile = f'{outputDir}/TsaThroughput.Cache.csv'
    logger.info(f'Saving Cache File for Later Processing: {outputFile}')
    csv_export = df.to_csv(outputFile, index=False)

    return df
    
def pivotDataframe(df):
    df = df.pivot_table(index=['Date','Hour'], columns=['AirportCode','CheckpointName'], values='Amount').reset_index()
    df.columns = [' '.join(col).strip() for col in df.columns.values]
    return df


def getOutputFile(inputFile, airportCode, ext):
    """
    Constructs an output file name fron the given input file
    """
    basename = os.path.basename(inputFile)
    splitExt = os.path.splitext(basename)
    outputFile = f'{airportCode}-' + splitExt[0] + ext

    return outputFile


if __name__ == '__main__':
    #  python make_airport_dataset.py dir -d ../../../../data/raw/tsa/throughput -a SEA -o ../../../../data/processed/tsa/throughput 
    #  python make_airport_dataset.py file -i ../../../../data/raw/tsa/throughput/tsa_throughput_march_3-9_2019.json -a SEA -o ../../../../data/processed/tsa/throughput

    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    logger = logging.getLogger(__name__)
    logger.info('Making final data set from raw data.')

    parser = ArgumentParser()
    subParser = parser.add_subparsers()
    subParserRequired = True
    subParser.dest = 'file or dir or csv'
    
    fileParser = subParser.add_parser('file',      help = 'Process a single file')
    fileParser.add_argument('-f', '--inputFile',   help = 'The full path and filename for the input file')
    fileParser.add_argument('-a', '--airportCode', help = 'The Airport Code to filter dataset by')
    fileParser.add_argument('-o', '--outputDir',   help = 'The output directory to write the file')
    fileParser.set_defaults(func=processFile)

    dirParser = subParser.add_parser('dir',                   help = 'Process all files in a directory')
    dirParser.add_argument('-d', '--inputDir',                help = 'The path to the directory to process')
    dirParser.add_argument('-a', '--airportCode', nargs='?',  help = 'The Airport Code to filter dataset by')
    dirParser.add_argument('-o', '--outputDir',               help = 'The output directory to write the file')
    dirParser.add_argument('-m', '--matchString', nargs='?',  help = 'The string to search for the filename')
    dirParser.set_defaults(func=processDir)

    csvParser = subParser.add_parser('csv',                   help = 'Process an existing CSV file. Usually TsaThroughput.All.csv')
    csvParser.add_argument('-f', '--inputFile',                help = 'The path to the directory to process')
    csvParser.add_argument('-a', '--airportCode', nargs='?',  help = 'The Airport Code to filter dataset by')
    csvParser.add_argument('-o', '--outputDir',               help = 'The output directory to write the file')
    csvParser.set_defaults(func=processCsv)

    args = parser.parse_args()
    
    # Based on command line input, we'll either process a single file, whole directory or a csv file
    if args.func.__name__ == 'processFile':
        processFile(args.inputFile, args.airportCode, args.outputDir, logger)
    elif(args.func.__name__ == 'processDir'):
        processDir(args.inputDir, args.matchString, args.airportCode, args.outputDir, logger)
    else:
        processCsv(args.inputFile, args.airportCode, args.outputDir, logger)

