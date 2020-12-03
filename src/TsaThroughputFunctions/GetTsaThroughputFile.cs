using System;
using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Host;
using Microsoft.Extensions.Logging;
using HtmlAgilityPack;

namespace TsaThroughput.Data.Raw
{
    public static class GetTsaThroughputFile
    {
        [FunctionName("GetTsaThroughputFile")]
        public static void Run([TimerTrigger("0 * */30 * * *")]TimerInfo myTimer, ILogger log)
        {
            //string s = await GetLatestFiles();
            //log.LogInforamtion($"File: {s}");
            log.LogInformation($"C# Timer trigger function executed at: {DateTime.Now}");
        }
        
        public static async Task<string> GetLatestFiles() {
            var latestFile = await GetLatestThroughputFile();

            return latestFile;
        }

        public static async Task<string> GetLatestThroughputFile() {
            string website = "https://www.tsa.gov/foia/readingroom";

            HttpClient client = new HttpClient();
            string html = await client.GetStringAsync(website);

            HtmlDocument doc = new HtmlDocument();
            doc.LoadHtml(html); 

            var file = doc.DocumentNode
                .SelectSingleNode("//td/a[@class=foia-reading-link]");

            var url = file
                .Attributes["href"].Value;

            var title = file
                .InnerText;

            return $"<p><a href=\"{website}{url}\">{title}</a></p>";
        }
    }
}
