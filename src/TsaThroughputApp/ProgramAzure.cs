using System;
using System.Collections.Generic;
using System.CommandLine;
using System.CommandLine.Invocation;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading.Tasks;


using Azure;
using Azure.AI.FormRecognizer;
using Azure.AI.FormRecognizer.Models;
using Azure.AI.FormRecognizer.Training;

using TsaThroughputApp.Models;

namespace TsaThroughputApp
{
    class ProgramFormRecognizer
    {
        public static async Task<int> MainAzure(string[] args)
        {

            var rootCommand = new RootCommand
            {
                new Argument<string>(
                    "inputFile",
                    "The input file to parse"
                ),
                new Argument<string>(
                    "outputFile",
                    "The output file to write"
                )
            };

            rootCommand.Description = "Parses a Tsa Throughput File from PDF to JSON";

            string tsaThroughputInputFile = "";
            string tsaThroughputOutputFile = "";
           
            rootCommand.Handler = CommandHandler.Create<string, string>(async (inputFile, outputFile) =>
            {
                tsaThroughputInputFile = inputFile;
                tsaThroughputOutputFile = outputFile;

                // Setup the Form Recognizer Client
                var formRecognizerEndpointUri = new Uri(Environment.GetEnvironmentVariable("formRecognizerEndpointUri"));
                var formRecognizerCredential = new AzureKeyCredential(Environment.GetEnvironmentVariable("formRecognizerApiKey"));
                var client = new FormRecognizerClient(formRecognizerEndpointUri, formRecognizerCredential, new FormRecognizerClientOptions(FormRecognizerClientOptions.ServiceVersion.V2_0));
        
                TsaThroughput tsaThroughput = new TsaThroughput()
                {
                    Airports = new List<Airport>()
                };

                Airport airport = new Airport();
                Checkpoint checkpoint;
                string currentDateString = string.Empty;
                string currentHourString = string.Empty;

                using FileStream stream = new FileStream(tsaThroughputInputFile, FileMode.Open);

                FormPageCollection formPages = await client.StartRecognizeContent(stream).WaitForCompletionAsync();
                foreach (FormPage page in formPages)
                {
                    for (int i = 0; i < page.Tables.Count; i++)
                    {
                        FormTable table = page.Tables[i];
                        int cellCursor = 0;

                        // Skip the first row of the table, as it contains titles
                        if (table.Cells[cellCursor].RowIndex == 0)
                            cellCursor += 7;

                        // Loop through the cells until the end
                        while (cellCursor < table.Cells.Count)
                        {
                            switch (table.Cells[cellCursor].ColumnIndex)
                            {
                                // Date
                                case 0:
                                    // Sometimes the date spans more than one cell. Especially in the case of 2 digit months and days.
                                    // In this case it will return a string like "11/22/202 0"
                                    //   We remove spaces to handle this case
                                    // In other cases it may pick up the 0 on the second line as a new date
                                    //   To handle this, we only update the date if it parses to a valid date otherwise, we continue with the previous vlue
                                    DateTime currentDate;
                                    if(DateTime.TryParse(Regex.Replace(table.Cells[cellCursor++].Text, @"\s+", ""), out currentDate))
                                    {
                                        currentDateString = currentDate.ToString("MM/dd/yyyy");
                                    }
                                    break;

                                // Hour
                                case 1:
                                    currentHourString = table.Cells[cellCursor++].Text;
                                    break;

                                // Airport
                                case 2:
                                    airport = CreateAirport(table.Cells, currentDateString, currentHourString, ref cellCursor);
                                    Airport existingAirport = tsaThroughput.Airports.Find(a => a.AirportCode.Equals(airport.AirportCode));
                                    if(existingAirport != null)
                                    {
                                        // See if the day already exists for this airport
                                        Day existingDay = existingAirport.Days.Find(d => d.Date.Equals((airport.Days.First<Day>()).Date));
                                        if(existingDay != null)
                                        {
                                            // See if the checkpoint exists for this airport
                                            Checkpoint existingCheckpoint = existingDay.Checkpoints.Find(c => c.CheckpointName.Equals(airport.Days.First<Day>().Checkpoints.First<Checkpoint>().CheckpointName));
                                            if(existingCheckpoint != null)
                                            {
                                                existingCheckpoint.Hours.Add(airport.Days.First<Day>().Checkpoints.First<Checkpoint>().Hours.First<Throughput>());
                                            }
                                            else
                                            {
                                                existingDay.Checkpoints.Add(airport.Days.First<Day>().Checkpoints.First<Checkpoint>());
                                            }
                                        }
                                        else
                                        {
                                            existingAirport.Days.Add(airport.Days.First<Day>());
                                        }
                                    }
                                    else
                                    {
                                        tsaThroughput.Airports.Add(airport);
                                    }
                                    break;

                                // Checkpoint
                                case 6:
                                    // Instantiate a checkpoint object from the current cell
                                    checkpoint = CreateCheckpoint(table.Cells, currentDateString, currentHourString, ref cellCursor);

                                    // Get the associated airport from our master list of airports.
                                    existingAirport = tsaThroughput.Airports.Find(a => a.AirportCode.Equals(airport.AirportCode));

                                    if(existingAirport != null)
                                    {
                                        // Get the checkpoint for the last day loaded
                                        Day curDay = existingAirport.Days.Last<Day>();
                                        Checkpoint curCheckpoint = curDay.Checkpoints.Find(c => c.CheckpointName.Equals(checkpoint.CheckpointName));
                                        if (curCheckpoint != null)
                                        {
                                            curCheckpoint.Hours.Add(checkpoint.Hours.First<Throughput>());
                                        }
                                        else
                                        {
                                            curDay.Checkpoints.Add(checkpoint);
                                        }
                                    }
                                    else
                                    {
                                        // We shouldn't get here, but lets write it out just in case
                                        Console.WriteLine($"Unable to retrieve airport for Checkpoint: {currentDateString}/{currentHourString}/{airport.AirportCode}/{checkpoint.CheckpointName}");
                                    }
                                    break;

                                default:
                                {
                                    // We're not supposed to get here, but sometimes the form recognizer will recognize the second line
                                    // in two line row as a new cell. For now we'll write out the offending cell and
                                    // increment the cellCursor which should get us on track
                                    // TODO: Append the text to the proper field. This only occurs in AirportName so far.
                                    Console.WriteLine($"{page.PageNumber}/{currentHourString}/{cellCursor}/{table.Cells[cellCursor].ColumnIndex}/{table.Cells[cellCursor].Text}");
                                    cellCursor++;
                                    break;
                                }
                            }
                        }
                    }
                }

                using FileStream fs = File.Create(tsaThroughputOutputFile);
                await JsonSerializer.SerializeAsync(fs, tsaThroughput);

                Console.WriteLine($"Processed {formPages.Count} Pages.");
                Console.WriteLine($"Airports: {tsaThroughput.Airports.Count}");
            });
            
            return await Task.FromResult<int>(rootCommand.InvokeAsync(args).Result);
        }

        private static Airport CreateAirport(IReadOnlyList<FormTableCell> cells, string currentDateString, string currentHourString, ref int cellCursor)
        {
            Airport airport = new Airport()
            {
                AirportCode = cells[cellCursor++].Text,
                AirportName = cells[cellCursor++].Text,
                City = cells[cellCursor++].Text,
                State = cells[cellCursor++].Text,

                Days = new List<Day>()
            };

            Checkpoint checkpoint = CreateCheckpoint(cells, currentDateString, currentHourString, ref cellCursor);

            Day day = new Day()
            {
                Date = DateTime.Parse(currentDateString),

                Checkpoints = new List<Checkpoint>()
            };

            day.Checkpoints.Add(checkpoint);
            airport.Days.Add(day);

            return airport;
        }

        private static Checkpoint CreateCheckpoint(IReadOnlyList<FormTableCell> cells, string currentDateString, string currentHourString, ref int cellCursor)
        {
            Checkpoint checkpoint = new Checkpoint()
            {
                CheckpointName = cells[cellCursor++].Text,

                Hours = new List<Throughput>()
            };

            try
            {
                Throughput throughput = new Throughput()
                {
                    Hour = DateTime.Parse(currentDateString) + TimeSpan.Parse(currentHourString),
                    Amount = int.Parse(cells[cellCursor++].Text, NumberStyles.AllowThousands)
                };

                checkpoint.Hours.Add(throughput);
            }
            catch(System.FormatException e)
            {
                Console.WriteLine($"{e.Message}");
            }
            return checkpoint;
        }
    }
}