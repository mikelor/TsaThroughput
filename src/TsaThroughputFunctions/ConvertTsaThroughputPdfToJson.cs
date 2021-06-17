// Default URL for triggering event grid function in the local environment.
// http://localhost:7071/runtime/webhooks/EventGrid?functionName={functionname}

using Microsoft.Azure.WebJobs;
using Microsoft.Azure.EventGrid.Models;
using Microsoft.Azure.WebJobs.Extensions.EventGrid;
using Microsoft.Extensions.Logging;


namespace TsaThroughput.Data.Raw
{
    public static class ConvertTsaThroughputPdfToJson
    {
        [FunctionName("ConvertTsaThroughputPdfToJson")]
        public static void Run([EventGridTrigger]EventGridEvent eventGridEvent, ILogger log)
        {
            log.LogInformation($"Event received {eventGridEvent.EventType} {eventGridEvent.Subject}");
        }
    }
}
