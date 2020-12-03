using System;
using System.Threading;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Host;
using Microsoft.Extensions.Logging;

namespace TsaThroughput.Data.Raw
{
    public static class GetTsaThroughputFile
    {
        [FunctionName("GetTsaThroughputFile")]
        public static void Run([TimerTrigger("0 * */30 * * *")]TimerInfo myTimer, ILogger log)
        {
            string s = await GetlatestFiles();
            log.LogInforamtion($"File: {s}");
            log.LogInformation($"C# Timer trigger function executed at: {DateTime.Now}");
        }
        
        public static async Task<string> GetLatestFiles() {
            var latestFile = await GetlatestFile();

            return latestFile;
        }

        public static async Task<string> GetlatestFile() {
            string website = "https://www.tsa.gov/foia/readingroom";

            HttpClient client = new HttpClient();
            string html = await client.GetStringAsync(website);

            HtmlDocument doc = new HtmlDocument();
            doc.LoadHtml(html); 

            var file = doc.DocumentNode
                .SelectNodes("//a")
                .FirstOrDefault(x => x.Attributes.Contains("class") && x.Attributes["class"].Value.Contains("foia-reading-link"));

            var url = file
                .Attributes
                .FirstOrDefault(x => x.Name == "href")
                .Value;

            var title = file
                .SelectSingleNode("//td/a")
                .InnerHtml;

            return $"<p><a href=\"{website}{url}\">{title}</a></p>";
        }
    }
}
