using System.Runtime.CompilerServices;
using TsaThroughput.Core.Models;

namespace TsaThroughput.Core.Extracters
{
    public enum PdfExtractionEngine
    {
        TabulaSharp,
        AzureFormRecognizer
    }

    /// <summary>
    /// The 'Strategy' abstract class
    /// </summary>
    public interface IExtractionStrategy
    {
        public abstract Task<TsaThroughputRoot> Extract(string inputFile);
    }

    public class ExtractionContext
    {
        readonly IExtractionStrategy strategy;


        public ExtractionContext(PdfExtractionEngine pdfExtractionEngine)
        {
            switch(pdfExtractionEngine)
            { 
                case PdfExtractionEngine.TabulaSharp:
                    this.strategy = new TabulaSharpExtraction();
                    break;

                case PdfExtractionEngine.AzureFormRecognizer: 
                    this.strategy = new AzureFormRecognizerExtraction();
                    break;
                default:
                    this.strategy = new TabulaSharpExtraction();
                    break;
                    
            }
        }


        public async Task<TsaThroughputRoot> ExtractionContextInterface(string inputFile)
        {
            return await strategy.Extract(inputFile);
        }
    }
}
