using System.IO.Compression;

using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

using HtmlAgilityPack;


namespace TsaThroughput.Data.Raw
{
    public class GetTsaThroughputFile
    {
        private readonly ILogger _logger;
        private static readonly HttpClient _httpClient = new HttpClient();


        public GetTsaThroughputFile(ILoggerFactory loggerFactory)
        {
            _logger = loggerFactory.CreateLogger<GetTsaThroughputFile>();
        }

        [Function("GetTsaThroughputFile")]
        [BlobOutput("data/stage/tsa/throughput/{rand-guid}.pdf", Connection = "AzureWebJobsStorage")]
        public async Task<byte[]> RunAsync(
            [TimerTrigger("1/1 * * * *")] MyInfo myTimer,
            FunctionContext context)
        {
           // BlobOutputAttribute attribute = context.FunctionDefinition.OutputBindings.Queryable.First<BlobOutputAttribute>();
 
            _logger.LogInformation($"C# Timer trigger function executed at: {DateTime.Now}");
            _logger.LogInformation($"Next timer schedule at: {myTimer.ScheduleStatus.Next}");

            var latestThroughputFileUrl = await GetLatestThroughputFileUrl();
            var pdfFilename = latestThroughputFileUrl.Substring(latestThroughputFileUrl.LastIndexOf('/') + 1);
            _logger.LogInformation($"Latest throughputfiles {latestThroughputFileUrl}");

            var pdf = await SaveThroughputPdfAsync(latestThroughputFileUrl);
            return pdf;
        }

        //
        // GetLatestThroughputFileUrl(log)
        // Returns the Url of the latest TsaThroughputFile
        private static async Task<string> GetLatestThroughputFileUrl()
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
        private static async Task<byte[]> SaveThroughputPdfAsync(string url)
        {
            using var request = new HttpRequestMessage(HttpMethod.Get, new Uri(url));
            request.Headers.TryAddWithoutValidation("Accept", "application/pdf");
            request.Headers.TryAddWithoutValidation("User-Agent", "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0");

            using var response = await _httpClient.SendAsync(request).ConfigureAwait(false);
            response.EnsureSuccessStatusCode();

            byte [] byteArray = await response.Content.ReadAsByteArrayAsync();
            return byteArray;
        }
    }

    public class MyInfo
    {
        public MyScheduleStatus ScheduleStatus { get; set; }

        public bool IsPastDue { get; set; }
    }

    public class MyScheduleStatus
    {
        public DateTime Last { get; set; }

        public DateTime Next { get; set; }

        public DateTime LastUpdated { get; set; }
    }

}
