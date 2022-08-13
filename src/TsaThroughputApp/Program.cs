using System.CommandLine;
using System.CommandLine.Invocation;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;

using TsaThroughput.Core.Converters;
using TsaThroughput.Core.Models;


namespace TsaThroughputApp
{
    class Program
    {
        public static async Task<int> Main(string[] args)
        {

            var rootCommand = new RootCommand
            {
                new Argument<string>(
                    "converter",
                    "The algorithm to use for conversion FormRecognizer || TabulaSharp"
                ),
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

            string tsaConverter = "Tabula-Sharp";
            string tsaThroughputInputFile = "";
            string tsaThroughputOutputFile = "";


            rootCommand.Handler = CommandHandler.Create<string, string, string>(async (converter, inputFile, outputFile) =>
            {
                tsaConverter = converter;
                tsaThroughputInputFile = inputFile;
                tsaThroughputOutputFile = outputFile;

                ConverterStrategy strategy;
                switch(tsaConverter)
                {
                    case "TabulaSharp":
                        strategy = new TabulaSharpConverter();
                        break;
                    case "AzureFormRecognizer":
                        strategy = new AzureFormRecognizerConverter();
                        break;
                    default:
                        strategy = new TabulaSharpConverter();
                        break;
                }
                ConverterContext context = new (strategy);
                TsaThroughputRoot tsaThroughput = await context.ConverterContextInterface(inputFile, outputFile);
                
                using FileStream fs = File.Create(tsaThroughputOutputFile);
                await JsonSerializer.SerializeAsync(fs, tsaThroughput);
            });

            return await Task.FromResult<int>(rootCommand.InvokeAsync(args).Result);
        }
    }
}