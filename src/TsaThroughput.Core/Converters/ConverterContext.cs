using TsaThroughput.Core.Models;

namespace TsaThroughput.Core.Converters
{
    /// <summary>
    /// The 'Strategy' abstract class
    /// </summary>
    public interface ConverterStrategy
    {
        public abstract Task<TsaThroughputRoot> Convert(string inputFile, string outputFile);
    }

    public class ConverterContext
    {
        ConverterStrategy strategy;


        public ConverterContext(ConverterStrategy strategy)
        {
            this.strategy = strategy;

        }

        public async Task<TsaThroughputRoot> ConverterContextInterface(string inputFile, string outputFile)
        {
            return await strategy.Convert(inputFile, outputFile);
        }
    }
}
