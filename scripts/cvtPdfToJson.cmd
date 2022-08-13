@echo off 
setlocal
REM usage cvtPdfToJson <filename>
set _filename=%~n1
set _extension=%~x1
echo %_filename%
dotnet run --project ../src/TsaThroughputApp/ TabulaSharp ../data/%_filename%.pdf ../data/raw/tsa/throughput/%_filename%.json
endlocal  