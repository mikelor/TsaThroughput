import json
from datetime import datetime
from dotenv import find_dotenv, load_dotenv
import logging
import os
import pandas
from pathlib import Path
from argparse import ArgumentParser

def processFile(inputFile, logger):
    """
    Processes a single file
    """
    logger.info(f'Processing file: {inputFile}')
    
    df = processSingleFile(inputFile)

    df = postProcessDataframe(df)

    outputFile = getOutputFile(inputFile, '.csv')

    logger.info(f'Output file: {outputFile}')
    csv_export = df.to_csv(outputFile, index=False)


def processDir(inputDir, logger):
    """
    Processes a group of files in a directory
    """
    logger.info(f'Processing all files in: {inputDir}')

    numFilesProcessed = 0

    for entry in os.scandir(inputDir):
        if (entry.path.endswith(".json")) and entry.is_file():

            logger.info(f'Processing file: {entry.path}')

            if(numFilesProcessed == 0):
                logger.info('Processing First File')
                df = processSingleFile(entry.path)
            else:
                logger.info('Processing Other Files')
                df = df.append(processSingleFile(entry.path), ignore_index=True)
                
            
            numFilesProcessed += 1
            
    df = postProcessDataframe(df)

    # Output the file
    now = datetime.now()
    outputFile = f'{inputDir}/processed/tsa/throughput/sea-{datetime.now().strftime("%Y%m%d%H%M%S")}.csv'

    logger.info(f'[{numFilesProcessed}] Files Processed.')
    logger.info(f'Output file: {outputFile}')

    csv_export = df.to_csv(outputFile, index=False)
    

def processSingleFile(file):
    
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

    df = df[df['Airports.AirportCode'] == 'SEA']
    df = df.pivot_table(index=['Airports.Days.Date','Hour'], columns=['Airports.AirportCode','Airports.Days.Checkpoints.CheckpointName'], values='Amount').reset_index()

    return df

def postProcessDataframe(df):
    df.columns = [' '.join(col).strip() for col in df.columns.values]
    df.sort_values(by=['Airports.Days.Date','Hour'], inplace=True)
    print(df)

    return df


def getOutputFile(inputFile, ext):
    """
    Constructs an output file name fron the given input file
    """
    splitText = os.path.splitext(inputFile)
    outputFile = splitText[0] + ext

    return outputFile


if __name__ == '__main__':
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
    
    fileParser = subParser.add_parser('file', help='Process a single file')
    fileParser.add_argument("-i", "--inputFile", help = "The full path and filename for the input file")
    fileParser.set_defaults(func=processFile)

    dirParser = subParser.add_parser('dir', help='Process all files in a directory')
    dirParser.add_argument("-d", "--inputDir", help = "The path to the directory to process")
    dirParser.set_defaults(func=processDir)

    args = parser.parse_args()
    
    # Based on command line input, we'll either process a single file or a whole directory
    if args.func.__name__ == 'processFile':
        processFile(args.inputFile, logger)
    else:
        processDir(args.inputDir, logger)
