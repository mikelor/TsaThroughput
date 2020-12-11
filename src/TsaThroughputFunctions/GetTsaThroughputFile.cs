using System;
using System.IO;
using System.IO.Compression;
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
        private static readonly HttpClient _httpClient = new HttpClient();

        [FunctionName("GetTsaThroughputFile")]
        public static async void Run([TimerTrigger("1/1 * * * *")]TimerInfo myTimer, ILogger log) {
            log.LogInformation($"C# Timer trigger function executed at: {DateTime.Now}");
            var latestThroughputFile = await GetLatestThroughputFile(log);
            log.LogInformation($"Latest throughputfiles is {latestThroughputFile}");
        }

        private static async Task<string> GetAsyncString(string url)
        {
            // Need to impersonate a browser, otherwise HTTP 403 Forbidden is returned
            // See https://stackoverflow.com/questions/15026953/httpclient-request-like-browser/15031419#15031419
            using (var request = new HttpRequestMessage(HttpMethod.Get, new Uri(url))) {
                request.Headers.TryAddWithoutValidation("Accept", "text/html,application/xhtml+xml,application/xml");
                request.Headers.TryAddWithoutValidation("Accept-Encoding", "gzip, deflate");
                request.Headers.TryAddWithoutValidation("User-Agent", "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0");
                request.Headers.TryAddWithoutValidation("Accept-Charset", "ISO-8859-1");

                using (var response = await _httpClient.SendAsync(request).ConfigureAwait(false)) {
                    response.EnsureSuccessStatusCode();
                    using (var responseStream = await response.Content.ReadAsStreamAsync().ConfigureAwait(false))
                    using (var decompressedStream = new GZipStream(responseStream, CompressionMode.Decompress))
                    using (var streamReader = new StreamReader(decompressedStream)) {
                        return await streamReader.ReadToEndAsync().ConfigureAwait(false);
                    }
                }
            }
        }

        private static async Task<string> GetLatestThroughputFile(ILogger log) {
            string website = "https://www.tsa.gov/foia/readingroom";

            var html = await GetAsyncString(website);

            HtmlDocument doc = new HtmlDocument();
            doc.LoadHtml(html); 

            var file = doc.DocumentNode.SelectSingleNode("//td/a[@class=foia-reading-link]");
            var url = file.Attributes["href"].Value;
            var title = file.InnerText;

            return $"<p><a href=\"{website}{url}\">{title}</a></p>";
        }
    }
}
