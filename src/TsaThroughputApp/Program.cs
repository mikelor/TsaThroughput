using System.IO;
using System.Text.Json;
using System.Threading.Tasks;

using System.CommandLine;

using TsaThroughput.Core.Extracters;
using TsaThroughput.Core.Models;


namespace TsaThroughputApp
{

    class Program
    {
        public static async Task<int> Main(string[] args)
        {
            var pdfExtractionEngine = new Option<PdfExtractionEngine>(
                name: "--PdfExtractionEngine", 
                description: "The extraction engine to use in parsing the Pdf file.\nIn order to use the AzureFormRecognizer engine you will need to setup your own instance of Azure Form Recognizer.\nSee more at https://azure.microsoft.com/en-us/services/form-recognizer/",
                getDefaultValue: () => PdfExtractionEngine.TabulaSharp
                );

            var inputFile = new Argument<string>(
                "inputFile",
                "The TSA Throughput PDF file to extract data from. "
                );

            var outputFile = new Argument<string>(
                "outputFile",
                "The output file to write extracted data to."
                );

            var rootCommand = new RootCommand
            {
                pdfExtractionEngine,
                inputFile,
                outputFile
            };

            rootCommand.Description = "Extracts TSA Throughput Information from a PDF file and outputs it to a JSON file.\n\nThird Party Licenses: Tabula-Sharp https://github.com/BobLd/tabula-sharp/blob/master/LICENSE";
            rootCommand.SetHandler( async (pdfExtractionEngine, inputFile, outputFile) => 
                {
                    ExtractionContext context = new (pdfExtractionEngine);
                    TsaThroughputRoot tsaThroughput = await context.ExtractionContextInterface(inputFile);
                
                    using FileStream fs = File.Create(outputFile);
                    await JsonSerializer.SerializeAsync(fs, tsaThroughput);
                },
                pdfExtractionEngine,
                inputFile,
                outputFile
            );

            return await Task.FromResult<int>(rootCommand.InvokeAsync(args).Result);
        }
    }
}