namespace TsaThroughput.Core.Models
{
    public class Throughput
    {
        public DateTime Hour { get; set; }
        public int Amount { get; set; }
    }

    public class Checkpoint
    {
        public string CheckpointName { get; set; }
        public List<Throughput> Hours { get; set; }
    }

    public class Day
    {
        public DateTime Date { get; set; }
        public List<Checkpoint> Checkpoints { get; set; }
    }

    public class Airport
    {
        public string AirportCode { get; set; }
        public string AirportName { get; set; }
        public string City { get; set; }
        public string State { get; set; }
        public List<Day> Days { get; set; }
    }

    public class TsaThroughputRoot
    {
        public List<Airport> Airports { get; set; }
    }

}
