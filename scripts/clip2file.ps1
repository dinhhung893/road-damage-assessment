<#
.SYNOPSIS
    Save clipboard image to project data/screenshots/ directory.

.DESCRIPTION
    Captures the current clipboard image (from Snipping Tool, Win+Shift+S, etc.)
    and saves it as a timestamped PNG in the project's data/screenshots/ folder.
    The saved file path is copied to clipboard for easy paste into Cascade chat.

.EXAMPLE
    .\scripts\clip2file.ps1
    Saved: D:\Antigravity\New folder\dumps\data\screenshots\snip_20260521_220400.png
#>

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Project root = parent of scripts/ directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$saveDir = Join-Path $projectRoot "data\screenshots"

if (!(Test-Path $saveDir)) {
    New-Item -ItemType Directory -Path $saveDir -Force | Out-Null
}

if ([System.Windows.Forms.Clipboard]::ContainsImage()) {
    $image = [System.Windows.Forms.Clipboard]::GetImage()
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $filename = Join-Path $saveDir "snip_$timestamp.png"
    $image.Save($filename, [System.Drawing.Imaging.ImageFormat]::Png)

    # Copy file path to clipboard for easy paste into Cascade chat
    Set-Clipboard -Value $filename
    Write-Output "Saved: $filename"
    Write-Output "Path copied to clipboard — paste into Cascade chat to have it read the image."
} else {
    Write-Output "No image in clipboard. Use Win+Shift+S to snip first."
}
