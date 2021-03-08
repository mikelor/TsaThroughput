echo $1
dotnet run -p ../src/TsaThroughputApp/ ${1%.*}.pdf ${1%.*}.json