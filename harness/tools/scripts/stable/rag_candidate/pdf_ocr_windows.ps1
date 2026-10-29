param([Parameter(Mandatory=$true)][string]$Queue)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime]
$null = [Windows.Storage.Streams.IRandomAccessStream,Windows.Storage.Streams,ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.SoftwareBitmap,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime]
$null = [Windows.Media.Ocr.OcrResult,Windows.Foundation,ContentType=WindowsRuntime]
$null = [Windows.Globalization.Language,Windows.Globalization,ContentType=WindowsRuntime]
$taskMethod = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
} | Select-Object -First 1
function Await-Operation($Operation, [Type]$ResultType) {
    $task = $taskMethod.MakeGenericMethod($ResultType).Invoke($null, @($Operation))
    $task.Wait()
    return $task.Result
}
$jobs = Get-Content -LiteralPath $Queue -Encoding UTF8 -Raw | ConvertFrom-Json
foreach ($job in $jobs) {
    $stream = $null
    $bitmap = $null
    try {
        $language = New-Object Windows.Globalization.Language($job.language)
        $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($language)
        if ($null -eq $engine) { throw ('OCR language unavailable: ' + $job.language) }
        $file = Await-Operation ([Windows.Storage.StorageFile]::GetFileFromPathAsync($job.image)) ([Windows.Storage.StorageFile])
        $stream = Await-Operation ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
        $decoder = Await-Operation ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
        $bitmap = Await-Operation ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
        $result = Await-Operation ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
        $lines = @($result.Lines | ForEach-Object {
            @{text=$_.Text; words=@($_.Words | ForEach-Object {
                @{text=$_.Text; x=$_.BoundingRect.X; y=$_.BoundingRect.Y; w=$_.BoundingRect.Width; h=$_.BoundingRect.Height}
            })}
        })
        @{engine='Windows.Media.Ocr'; language=$job.language; text=$result.Text; lines=$lines; textAngle=$result.TextAngle} |
            ConvertTo-Json -Depth 8 -Compress | Set-Content -LiteralPath $job.output -Encoding UTF8
    } finally {
        if ($null -ne $bitmap) { $bitmap.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}
