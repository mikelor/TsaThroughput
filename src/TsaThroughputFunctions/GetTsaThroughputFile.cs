using System;
using System.IO;
using System.IO.Compression;
using System.Net.Http;
using System.Threading.Tasks;

using Microsoft.AspNetCore.Mvc;

using Microsoft.Azure.WebJobs;

using Microsoft.Extensions.Logging;

using HtmlAgilityPack;


namespace TsaThroughput.Data.Raw
{
    public static class GetTsaThroughputFile
    {
        private static readonly HttpClient _httpClient = new HttpClient();

        [FunctionName("GetTsaThroughputFile")]
        public static async Task Run(
            [TimerTrigger("1/1 * * * *")] TimerInfo myTimer,
            [Blob("data/stage/tsa/throughput/pdffile.pdf", FileAccess.Write, Connection = "AzureWebJobsStorage")] Stream pdfStream,
            ILogger log, 
            ExecutionContext context)
        {
            log.LogInformation($"C# Timer trigger function executed at: {DateTime.Now}");

            var latestThroughputFileUrl = await GetLatestThroughputFileUrl(log);
            log.LogInformation($"Latest throughputfiles is {latestThroughputFileUrl}");

            var pdf = await SaveThroughputPdfAsync(latestThroughputFileUrl);

            var pdfWriter = new StreamWriter(pdfStream);
            pdfWriter.Write(pdf);
            pdfWriter.Flush();
            log.LogInformation("Stream Saved");

        }

        //
        // GetLatestThroughputFileUrl(log)
        // Returns the Url of the latest TsaThroughputFile
        private static async Task<string> GetLatestThroughputFileUrl(ILogger log) 
        {
            string website = "https://www.tsa.gov";
            string subUrl = "/foia/readingroom/";

            var html = await GetAsyncString($"{website}{subUrl}");

            HtmlDocument doc = new HtmlDocument();
            doc.LoadHtml(html);

            // Extract the link so we can fetch it. Make sure it is a TSA Throughput File
            // This assumes that the first file is always the latest
            var url = doc.DocumentNode
                .SelectSingleNode("//a[@class='foia-reading-link'][contains(text(),'TSA Throughput')]")
                .Attributes["href"].Value;

            return $"{website}{url}";
        }

        //
        // GetAsyncString(url)
        // Returns a string representation of the webpage for the given URL
        private static async Task<string> GetAsyncString(string url)
        {
            // Need to impersonate a browser, otherwise HTTP 403 Forbidden is returned
            // See https://stackoverflow.com/questions/15026953/httpclient-request-like-browser/15031419#15031419
            using var request = new HttpRequestMessage(HttpMethod.Get, new Uri(url)); 
            request.Headers.TryAddWithoutValidation("Accept", "text/html,application/xhtml+xml,application/xml");
            request.Headers.TryAddWithoutValidation("Accept-Encoding", "gzip, deflate");
            request.Headers.TryAddWithoutValidation("User-Agent", "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0");
            request.Headers.TryAddWithoutValidation("Accept-Charset", "ISO-8859-1");

            using var response = await _httpClient.SendAsync(request).ConfigureAwait(false);
            
            response.EnsureSuccessStatusCode();

            using var responseStream = await response.Content.ReadAsStreamAsync().ConfigureAwait(false);
            using var decompressedStream = new GZipStream(responseStream, CompressionMode.Decompress);
            using var streamReader = new StreamReader(decompressedStream);

            return await streamReader.ReadToEndAsync().ConfigureAwait(false);
        }

        //
        // SaveThroughtputPdfAsync(url)
        // Saves the PDF at the given URL to blob storage
        private static async Task<string> SaveThroughputPdfAsync(string url)
        {
            using var request = new HttpRequestMessage(HttpMethod.Get, new Uri(url));
            request.Headers.TryAddWithoutValidation("Accept", "application/pdf");
            request.Headers.TryAddWithoutValidation("User-Agent", "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0");

            using var response = await _httpClient.SendAsync(request).ConfigureAwait(false);
            response.EnsureSuccessStatusCode();

            using var responseStream = await response.Content.ReadAsStreamAsync().ConfigureAwait(false);
            using var streamReader = new StreamReader(responseStream);

            string pdf = await streamReader.ReadToEndAsync().ConfigureAwait(false);
            return pdf;
        }


    }
}
