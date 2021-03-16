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
    logger.info(f'Processing file: {inputFile}')
    
    df = processSingleFile(inputFile, airportCode)

    df = postProcessDataframe(df)

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
    for entry in os.scandir(inputDir):
        if (entry.path.endswith('.json') and 
            entry.is_file()):

            # If a matchString was specified, let's ensure the entry matches
            if(not matchString or matchString in entry.path):

                logger.info(f'Processing file: {entry.path}')

                if(numFilesProcessed == 0):
                    logger.info(f'Processing first file: {entry.path}')
                    df = processSingleFile(entry.path, airportCode)
                else:
                    logger.info(f'Processing additional files: {entry.path}')
                    df = df.append(processSingleFile(entry.path, airportCode), ignore_index=True)
                
                numFilesProcessed += 1
            else:
                logger.info(f'Skipping file: {entry.path}')

        else:
            logger.info(f'Skipping file: {entry.path}')
   
    logger.info(f'Files Processed: [{numFilesProcessed}].')
        
    # If we processed at least one file, process the dataframe and write out the file
    if (numFilesProcessed > 0):
        df = postProcessDataframe(df)


        # Generate outputFile path
        now = datetime.now()
        outputFile = f'{outputDir}/{airportCode}-{datetime.now().strftime("%Y%m%d%H%M%S")}.csv'

        logger.info(f'Output file: {outputFile}')
        csv_export = df.to_csv(outputFile, index=False)
    else:
        logger.info(f'No output file created.')
     

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

    df = df[df['Airports.AirportCode'] == airportCode]
    df = df.pivot_table(index=['Airports.Days.Date','Hour'], columns=['Airports.AirportCode','Airports.Days.Checkpoints.CheckpointName'], values='Amount').reset_index()

    df = df.rename(columns =
        {
            'Airports.Days.Date' : 'Date', 
            'Airports.AirportCode' : 'AirportCode', 
            'Airports.Days.Checkpoints.CheckpointName' : 'CheckpointName'
        }, 
        inplace=False)
  
    return df

def postProcessDataframe(df):
    df.columns = [' '.join(col).strip() for col in df.columns.values]
    df.sort_values(by=['Date','Hour'], inplace=True)
    print(df)

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
    #  python make_sea_dataset.py dir -d ../../../../data/raw/tsa/throughput -a SEA

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
    subParser.dest = 'file or dir'
    
    fileParser = subParser.add_parser('file',      help = 'Process a single file')
    fileParser.add_argument('-i', '--inputFile',   help = 'The full path and filename for the input file')
    fileParser.add_argument('-a', '--airportCode', help = 'The Airport Code to filter dataset by')
    fileParser.add_argument('-o', '--outputDir',   help = 'The output directory to write the file')
    fileParser.set_defaults(func=processFile)

    dirParser = subParser.add_parser('dir',                   help = 'Process all files in a directory')
    dirParser.add_argument('-d', '--inputDir',                help = 'The path to the directory to process')
    dirParser.add_argument('-a', '--airportCode',             help = 'The Airport Code to filter dataset by')
    dirParser.add_argument('-o', '--outputDir',               help = 'The output directory to write the file')
    dirParser.add_argument('-m', '--matchString', nargs='?',  help = 'The string to search for the filename')
    dirParser.set_defaults(func=processDir)

    args = parser.parse_args()
    
    # Based on command line input, we'll either process a single file or a whole directory
    if args.func.__name__ == 'processFile':
        processFile(args.inputFile, args.airportCode, args.outputDir, logger)
    else:
        processDir(args.inputDir, args.matchString, args.airportCode, args.outputDir, logger)
