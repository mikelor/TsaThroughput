using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text.Json;
using System.Threading.Tasks;


using Azure;
using Azure.AI.FormRecognizer;
using Azure.AI.FormRecognizer.Models;
using Azure.AI.FormRecognizer.Training;

using TsaThroughputApp.Models;

namespace TsaThroughputApp
{
    class Program
    {
        static async Task Main(string[] args)
        {


            var credential = new AzureKeyCredential(apiKey);
            var client = new FormRecognizerClient(new Uri(endpoint), credential);

            string tsaThroughputFilePath = @"c:\users\mloreng\source\repos\tsathroughput\data\tsathroughput.pdf";

            TsaThroughput tsaThroughput = new TsaThroughput()
            {
                Airports = new List<Airport>()
            };

            Airport airport = new Airport();
            Checkpoint checkpoint;
            string currentDateString = string.Empty;
            string currentHourString = string.Empty;

            using FileStream stream = new FileStream(tsaThroughputFilePath, FileMode.Open);

            FormPageCollection formPages = await client.StartRecognizeContent(stream).WaitForCompletionAsync();
            foreach (FormPage page in formPages)
            {
                for (int i = 0; i < page.Tables.Count; i++)
                {
                    FormTable table = page.Tables[i];
                    int cellCursor = 0;

                    // Skip the first row of the table, as it contains titles
                    if (table.Cells[cellCursor].RowIndex == 0)
                        cellCursor += 8;

                    // Loop through the cells until the end
                    while (cellCursor < table.Cells.Count)
                    {
                        switch (table.Cells[cellCursor].ColumnIndex)
                        {
                            // Date
                            case 0:
                                currentDateString = table.Cells[cellCursor++].Text;
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
                                // Not needed as airport should always contain the last airport loaded
                                // airport = tsaThroughput.Airports.Find(a => a.AirportCode.Equals(airport.AirportCode));
                                checkpoint = CreateCheckpoint(table.Cells, currentDateString, currentHourString, ref cellCursor);

                                // Get the checkpoint for the last day loaded
                                Day curDay = airport.Days.Last<Day>();
                                Checkpoint curCheckpoint = curDay.Checkpoints.Find(c => c.CheckpointName.Equals(checkpoint.CheckpointName));
                                if (curCheckpoint != null)
                                {
                                    curCheckpoint.Hours.Add(checkpoint.Hours.First<Throughput>());
                                }
                                else
                                {
                                    curDay.Checkpoints.Add(checkpoint);
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

            using FileStream fs = File.Create(@"c:\users\mloreng\source\repos\tsathroughput\data\tsathroughput.json");
            await JsonSerializer.SerializeAsync(fs, tsaThroughput);

            Console.WriteLine($"Processed {formPages.Count} Pages.");
            Console.WriteLine($"Airports: {tsaThroughput.Airports.Count}");
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

            Throughput throughput = new Throughput()
            {
                Hour = DateTime.Parse(currentDateString) + TimeSpan.Parse(currentHourString),
                Amount = int.Parse(cells[cellCursor++].Text, NumberStyles.AllowThousands)
            };

            checkpoint.Hours.Add(throughput);

            return checkpoint;
        }
    }
}
