using System;
using System.Collections.Generic;
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

            string endpoint = "cog";
            string apiKey = "key";

            var credential = new AzureKeyCredential(apiKey);
            var client = new FormRecognizerClient(new Uri(endpoint), credential);

            string tsaThroughputFilePath = @"c:\users\mloreng\source\repos\tsathroughput\data\tsathroughputsmall.pdf";

            TsaThroughput tsaThroughput = new TsaThroughput()
            {
                Airports = new List<Airport>()
            };

            Airport airport = new Airport();
            Checkpoint checkpoint;

            using (FileStream stream = new FileStream(tsaThroughputFilePath, FileMode.Open))
            {
                string currentDateString = string.Empty;
                string currentHourString = string.Empty;



                FormPageCollection formPages = await client.StartRecognizeContent(stream).WaitForCompletionAsync();
                foreach (FormPage page in formPages)
                {
                    for (int i = 0; i < page.Tables.Count; i++)
                    {
                        FormTable table = page.Tables[i];
                        int cellCursor = 0;

                        while (cellCursor < table.Cells.Count)
                        {
                            // Skip the first row of the table, as it contains titles
                            if (table.Cells[cellCursor].RowIndex == 0)
                                cellCursor += 8;

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
                                    tsaThroughput.Airports.Add(airport);
                                    break;

                                // Checkpoint
                                case 6:
                                    airport = tsaThroughput.Airports.Find(a => a.AirportCode.Equals(airport.AirportCode));
                                    checkpoint = CreateCheckpoint(table.Cells, currentDateString, currentHourString, ref cellCursor);
                                    Day day = airport.Days.Last<Day>();
                                    break;

                            }
                        }
                    }
                }
            }
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

                Throughput = new List<Throughput>()
            };

            Throughput throughput = new Throughput()
            {
                Hour = DateTime.Parse(currentDateString) + TimeSpan.Parse(currentHourString),
                Amount = Int32.Parse(cells[cellCursor++].Text)
            };

            checkpoint.Throughput.Add(throughput);

            return checkpoint;
        }
    }
}
