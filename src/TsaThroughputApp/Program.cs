using System;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;


using Azure;
using Azure.AI.FormRecognizer;
using Azure.AI.FormRecognizer.Models;
using Azure.AI.FormRecognizer.Training;

namespace TsaThroughputApp
{
    class Program
    {
        static async Task Main(string[] args)
        {

            string endpoint = "https://<>.cognitiveservices.azure.com/";
            string apiKey = "<apikey>";

            var credential = new AzureKeyCredential(apiKey);
            var client = new FormRecognizerClient(new Uri(endpoint), credential);

            string tsaThroughputFilePath = @"c:\users\mloreng\source\repos\tsathroughput\data\tsathroughput.pdf";
            using (FileStream stream = new FileStream(tsaThroughputFilePath, FileMode.Open))
            {
                FormPageCollection formPages = await client.StartRecognizeContent(stream).WaitForCompletionAsync();
                foreach (FormPage page in formPages)
                {
                    Console.WriteLine($"Form Page {page.PageNumber} has {page.Lines.Count} lines.");

                    for (int i = 0; i < page.Lines.Count; i++)
                    {
                        FormLine line = page.Lines[i];
                        Console.WriteLine($"    Line {i} has {line.Words.Count} word{(line.Words.Count > 1 ? "s" : "")}, and text: '{line.Text}'.");
                    }

                    for (int i = 0; i < page.Tables.Count; i++)
                    {
                        FormTable table = page.Tables[i];
                        Console.WriteLine($"Table {i} has {table.RowCount} rows and {table.ColumnCount} columns.");
                        foreach (FormTableCell cell in table.Cells)
                        {
                            Console.WriteLine($"    Cell ({cell.RowIndex}, {cell.ColumnIndex}) contains text: '{cell.Text}'.");
                        }
                    }
                }
            }
        }
    }
}
