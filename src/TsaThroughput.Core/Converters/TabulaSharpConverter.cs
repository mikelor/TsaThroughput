using Microsoft.VisualBasic;
using System.Diagnostics;
using System.Globalization;
using System.Text.RegularExpressions;


using Tabula;
using Tabula.Extractors;
using UglyToad.PdfPig;

using TsaThroughput.Core.Models;
using Azure.AI.FormRecognizer.Models;

namespace TsaThroughput.Core.Converters
{
    enum CellType
    {
        Blank = 0,
        Date = 1,
        Time = 2,
        Airport = 4,
        Checkpoint = 5
    };


    public class TabulaSharpConverter : ConverterStrategy
    {
        public async Task<TsaThroughputRoot> Convert(string inputFile, string outputFile)
        {
            // Setup the root node for the Json file
            TsaThroughputRoot tsaThroughput = new()
            {
                Airports = new List<Airport>()
            };

            // Setup the Airport 
            Airport airport = new();
            Checkpoint checkpoint;
            string currentDateString = string.Empty;
            string currentHourString = string.Empty;
            int pageCount = 0;

            // Use Tabula
            using (PdfDocument document = PdfDocument.Open(inputFile, new ParsingOptions() { ClipPaths = false }))
            {
                IExtractionAlgorithm ea = new SpreadsheetExtractionAlgorithm();

                ObjectExtractor oe = new(document);
                PageIterator pageIterator = oe.Extract();

                while (pageIterator.MoveNext())
                {
                    var page = pageIterator.Current;
                    pageCount++;

                    List<Table> tables = ea.Extract(page);

                    int currentTable = 0;
                    foreach (Table table in tables)
                    {
                        currentTable++;

                        // Only look at tables with more than //TODO: 7? Columns
                        // This means we are looking at the table containing the data
                        if (table.ColumnCount > 7)
                        {
                            int currentRow = 0;
                            foreach (IReadOnlyList<Cell> row in table.Rows)
                            {


                                // Skip the table header row and footer row
                                int footerRow = 0;
                                if (currentRow > 0 && currentRow < (table.Rows.Count - footerRow))
                                {
                                    int currentCell = 0;

                                    // Enumerate through the list of cells. We chose to use an enumerator instead of a foreach loop so 
                                    // that we can advance to the next cell in the list within the inital enumeration.
                                    for (currentCell = 0; currentCell < row.Count - 1; currentCell++)
                                    {
                                        Cell cell = row[currentCell];
                                        Cell nextCell = row[currentCell + 1];

                                        switch (GetCellType(cell, nextCell))
                                        {
                                            case CellType.Blank:
                                                break;

                                            // Date
                                            case CellType.Date:
                                                // Sometimes the date spans more than one cell. Especially in the case of 2 digit months and days.
                                                // In this case it will return a string like "11/22/202 0"
                                                //   We remove spaces to handle this case
                                                // In other cases it may pick up the 0 on the second line as a new date
                                                //   To handle this, we only update the date if it parses to a valid date otherwise, we continue with the previous vlue
                                                DateTime currentDate;
                                                String dateString = row[currentCell].GetText();
                                                if (DateTime.TryParse(Regex.Replace(dateString, @"\s+", ""), out currentDate))
                                                {
                                                    currentDateString = currentDate.ToString("MM/dd/yyyy");
                                                }
                                                break;

                                            // Hour
                                            case CellType.Time:
                                                currentHourString = row[currentCell].GetText();
                                                break;

                                            case CellType.Airport:
                                                airport = AddAirport(tsaThroughput, row, currentDateString, currentHourString, ref currentCell);
                                                break;

                                            // Checkpoint
                                            case CellType.Checkpoint:
                                                // Instantiate a checkpoint object from the current cell
                                                checkpoint = AddCheckpoint(tsaThroughput, airport, row, currentDateString, currentHourString, ref currentCell);
                                                break;

                                            default:
                                                {
                                                    // We're not supposed to get here, but sometimes the form recognizer will recognize the second line
                                                    // in two line row as a new cell. For now we'll write out the offending cell and
                                                    // increment the cellCursor which should get us on track
                                                    // TODO: Append the text to the proper field. This only occurs in AirportName so far.
                                                    Console.WriteLine($"{page.PageNumber}/{currentHourString}/{currentCell}/{GetCellText(row, ref currentCell)}");
                                                    break;
                                                }

                                        }


                                    }
                                }
                                // On to the next row
                                currentRow++;
                                Debug.Print($"{currentDateString}:{currentHourString}:{airport.AirportName}");
                            }
                        }
                    }
                }
            }
            Console.WriteLine($"Processed {pageCount} Pages.");
            Console.WriteLine($"Airports: {tsaThroughput.Airports.Count}");
            return tsaThroughput;
        }

        private static CellType GetCellType(Cell cell, Cell nextCell)
        {
            CellType cellType = CellType.Blank;

            String cellText = cell.GetText();

            if (!cellText.Equals(""))
            {
                if (cellText.Length > 5 && DateTime.TryParse(Regex.Replace(cellText, @"\s+", ""), out _))
                {
                    cellType = CellType.Date;
                }
                else if (cellText.Length == 5 && cellText.Contains(':'))
                {
                    cellType = CellType.Time;
                }
                else if (cellText.Length == 3)
                {
                    if (Int32.TryParse(Regex.Replace(nextCell.GetText(), @",", ""), out _))
                    {
                        cellType = CellType.Checkpoint;
                    }
                    else
                    {
                        cellType = CellType.Airport;
                    }
                }
                else
                {
                    cellType = CellType.Checkpoint;
                }

            }

            return cellType;
        }


        private static string GetCellText(IReadOnlyList<Cell> row, ref int currentCell)
        {
            Cell cell = row[currentCell];
            string cellText = cell.GetText();
            currentCell++;

            // Somtimes a blank cell gets inserted and everything shifts right by 1
            // Lets continue until we find a non-blank cell;
            while (cellText.Equals(""))
            {
                if (currentCell < row.Count - 1)
                {
                    cell = row[currentCell];
                    cellText = cell.GetText();
                    currentCell++;
                }
                else
                {
                    Console.WriteLine("Ooops");
                    foreach (Cell c in row)
                    {
                        Console.Write($"[{c.GetText()}]");
                    }
                    Console.WriteLine();
                    break;
                }
            }

            return cellText;
        }

        private static Airport CreateAirport(IReadOnlyList<Cell> row, string currentDateString, string currentHourString, ref int currentCell)
        {

            Airport airport = new()
            {
                AirportCode = GetCellText(row, ref currentCell),
                AirportName = GetCellText(row, ref currentCell),
                City = GetCellText(row, ref currentCell),
                State = GetCellText(row, ref currentCell),

                Days = new List<Day>()
            };

            Checkpoint checkpoint = CreateCheckpoint(row, currentDateString, currentHourString, ref currentCell);

            Day day = new()
            {
                Date = DateTime.Parse(currentDateString),

                Checkpoints = new List<Checkpoint>()
            };

            day.Checkpoints.Add(checkpoint);
            airport.Days.Add(day);

            return airport;
        }

        private static Checkpoint CreateCheckpoint(IReadOnlyList<Cell> row, string currentDateString, string currentHourString, ref int currentCell)
        {
            Checkpoint checkpoint = new()
            {
                CheckpointName = GetCellText(row, ref currentCell),

                Hours = new List<Throughput>()
            };

            try
            {
                Throughput throughput = new()
                {
                    Hour = DateTime.Parse(currentDateString) + TimeSpan.Parse(currentHourString),
                    Amount = int.Parse(Regex.Replace(GetCellText(row, ref currentCell), @",", ""), NumberStyles.AllowThousands)
                };

                checkpoint.Hours.Add(throughput);
            }
            catch (System.FormatException e)
            {
                Console.WriteLine($"{e.Message}");
            }
            return checkpoint;
        }

        private static Airport AddAirport(TsaThroughputRoot tsaThroughput, IReadOnlyList<Cell> row, string currentDateString, string currentHourString, ref int currentCell)
        {
            Airport airport = CreateAirport(row, currentDateString, currentHourString, ref currentCell);
            currentCell--;

            Airport existingAirport = tsaThroughput.Airports.Find(a => a.AirportCode.Equals(airport.AirportCode));

            if (existingAirport != null)
            {
                // See if the day already exists for this airport
                Day existingDay = existingAirport.Days.Find(d => d.Date.Equals((airport.Days.First<Day>()).Date));
                if (existingDay != null)
                {
                    // See if the checkpoint exists for this airport
                    Checkpoint existingCheckpoint = existingDay.Checkpoints.Find(c => c.CheckpointName.Equals(airport.Days.First<Day>().Checkpoints.First<Checkpoint>().CheckpointName));
                    if (existingCheckpoint != null)
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

            return airport;
        }

        private static Checkpoint AddCheckpoint(TsaThroughputRoot tsaThroughput, Airport airport, IReadOnlyList<Cell> row, string currentDateString, string currentHourString, ref int currentCell)
        {
            // Instantiate a checkpoint object from the current cell
            Checkpoint checkpoint = CreateCheckpoint(row, currentDateString, currentHourString, ref currentCell);
            currentCell--;

            // Get the associated airport from our master list of airports.
            Airport existingAirport = tsaThroughput.Airports.Find(a => a.AirportCode.Equals(airport.AirportCode));

            if (existingAirport != null)
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
            return checkpoint;
        }

    }
}
