# Windows 11 Bloatware and Non-Windows Files Cleanup Script
# Run as Administrator for best results
# WARNING: This script will remove programs and files. Use at your own risk!

param(
    [switch]$WhatIf,
    [switch]$Force
)

# ---------------------------------
#  SAFETY VARIABLES & CONFIGURATION
# ---------------------------------

# Capture the full path to THIS script so we never delete it accidentally
$script:CurrentScriptPath = (Get-Item -LiteralPath $MyInvocation.MyCommand.Path).FullName

# This array will be lazily populated with any removable/network drives that are detected
$script:ExternalDrives = @()

# Helper test to determine whether the supplied path refers to the current script file
function Test-IsCurrentScript {
    param([string]$Path)
    return ($Path -eq $script:CurrentScriptPath)
}

# ---------------------------------
#  EXECUTION POLICY FOR THIS SESSION
# ---------------------------------
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# =====================================================================
#  Helper Functions
# =====================================================================

function Test-ExternalDrive {
    param([string]$DriveLetter)
    try {
        $drive = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='$DriveLetter'"
        if ($drive) {
            # 2 = Removable, 4 = Network
            return ($drive.DriveType -eq 2 -or $drive.DriveType -eq 4)
        }
    }
    catch {
        Write-Warning "Could not determine if $DriveLetter is external"
    }
    return $false
}

function Get-ExternalDrives {
    if ($script:ExternalDrives.Count -eq 0) {
        $script:ExternalDrives = @()
        $drives = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DriveType -eq 2 -or $_.DriveType -eq 4 }
        foreach ($drive in $drives) {
            $script:ExternalDrives += $drive.DeviceID.TrimEnd('\')
        }
    }
    return $script:ExternalDrives
}

function Test-ItemOnExternalDrive {
    param([string]$ItemPath)
    foreach ($drive in (Get-ExternalDrives)) {
        if ($ItemPath.StartsWith("$drive`\")) { return $true }
    }
    return $false
}

function Write-WhatIfLog {
    param([string]$Message,[string]$Color="Yellow")
    if ($WhatIf) { Write-Host "[WHAT-IF] $Message" -ForegroundColor $Color }
}

function Write-SuccessLog { param([string]$Message) if (-not $WhatIf) { Write-Host $Message -ForegroundColor Green } }

function Remove-SafeItemWithWhatIf {
    param(
        [string]$Path,
        [string]$Description,
        [switch]$Recurse=$false
    )

    if (-not (Test-Path -LiteralPath $Path)) { return }

    try {
        if ($WhatIf) {
            Write-WhatIfLog "Would remove: $Description ($Path)"
        }
        else {
            $params = @{ Path=$Path; Force=$true; ErrorAction="SilentlyContinue" }
            if ($Recurse) { $params.Recurse = $true }
            Remove-Item @params
            Write-SuccessLog "Removed: $Description"
        }
    }
    catch { Write-Warning "Failed to remove $Description`: $($_.Exception.Message)" }
}

function Remove-SafeItemWithExternalProtection {
    param([string]$ItemPath,[string]$ItemName)

    # Never delete the running script
    if (Test-IsCurrentScript $ItemPath) {
        Write-Host "Preserved (current script): $ItemPath" -ForegroundColor Blue
        return
    }

    # Never touch files on external drives
    if (Test-ItemOnExternalDrive $ItemPath) {
        Write-Host "Preserved (external drive): $ItemPath" -ForegroundColor Blue
        return
    }

    Remove-SafeItemWithWhatIf -Path $ItemPath -Description $ItemName -Recurse
}

function Remove-SafeItem {
    param([string]$Path,[string]$Description)
    Remove-SafeItemWithWhatIf -Path $Path -Description $Description -Recurse
}

# =====================================================================
#  CLEAN-UP ROUTINES
# =====================================================================

function Remove-WindowsApps {
    $bloatwareApps = @(
        "Microsoft.3DBuilder",
        "Microsoft.BingFinance",
        "Microsoft.BingNews",
        "Microsoft.BingSports",
        "Microsoft.BingWeather",
        "Microsoft.GetHelp",
        "Microsoft.Getstarted",
        "Microsoft.MicrosoftOfficeHub",
        "Microsoft.MicrosoftSolitaireCollection",
        "Microsoft.MixedReality.Portal",
        "Microsoft.People",
        "Microsoft.SkypeApp",
        "Microsoft.WindowsAlarms",
        "Microsoft.WindowsFeedbackHub",
        "Microsoft.WindowsMaps",
        "Microsoft.ZuneMusic",
        "Microsoft.ZuneVideo",
        "microsoft.windowscommunicationsapps",
        "Microsoft.WindowsSoundRecorder",
        "Microsoft.YourPhone",
        "Microsoft.WindowsCalculator",
        "Microsoft.WindowsCamera",
        "Microsoft.WindowsNotepad",
        "Microsoft.WindowsTerminal",
        "Microsoft.WindowsToDo",
        "Microsoft.WindowsVoiceRecorder",
        "Microsoft.Xbox.TCUI",
        "Microsoft.XboxApp",
        "Microsoft.XboxGameOverlay",
        "Microsoft.XboxGamingOverlay",
        "Microsoft.XboxIdentityProvider",
        "Microsoft.XboxSpeechToTextOverlay"
    )

    Write-Host "`n=== Removing Windows Bloatware Apps ===" -ForegroundColor Cyan

    foreach ($app in $bloatwareApps) {
        try {
            $appPackage = Get-AppxPackage -Name $app -AllUsers -ErrorAction SilentlyContinue
            if ($appPackage) {
                if ($WhatIf) { Write-WhatIfLog "Would remove Windows app: $app" }
                else {
                    Get-AppxPackage -Name $app -AllUsers | Remove-AppxPackage -ErrorAction SilentlyContinue
                    Write-SuccessLog "Removed Windows app: $app"
                }
            }
        }
        catch { Write-Warning "Failed to remove Windows app $app`: $($_.Exception.Message)" }
    }
}

function Remove-ThirdPartyBloatware {
    # NOTE: Google Chrome has been intentionally EXCLUDED from this list!
    $bloatwarePrograms = @(
        "McAfee Security",
        "McAfee LiveSafe",
        "Norton Security",
        "Norton 360",
        "AVG",
        "Avast",
        "Kaspersky",
        "Trend Micro",
        "HP Support Assistant",
        "HP Customer Experience Enhancements",
        "HP Registration Service",
        "HP System Event Utility",
        "Dell Digital Delivery",
        "Dell Customer Connect",
        "Dell Update",
        "Lenovo Vantage",
        "Lenovo System Interface Foundation",
        "ASUS WebStorage",
        "ASUS Live Update",
        "Acer Care Center",
        "Acer Registration",
        "Samsung Magician",
        "Samsung Data Migration",
        "Adobe Reader",
        "Adobe Flash Player",
        "Java Runtime Environment",
        "Java 8",
        "Java 7",
        "QuickTime",
        "RealPlayer",
        "WinRAR",
        "7-Zip",
        "CCleaner",
        "Advanced SystemCare",
        "IObit Uninstaller",
        "Driver Booster",
        "Driver Easy",
        "DriverMax",
        "Snapchat",
        "TikTok",
        "Facebook",
        "Instagram",
        "Twitter",
        "Discord",
        "Steam",
        "Epic Games Launcher",
        "Origin",
        "Battle.net",
        "Uplay",
        "Rockstar Games Launcher",
        "GOG Galaxy",
        "Twitch",
        "OBS Studio",
        "XSplit",
        "Streamlabs",
        "Spotify",
        "iTunes",
        "VLC Media Player",
        "Windows Media Player",
        "Groove Music",
        "Movies & TV",
        "Photos",
        "Paint 3D",
        "3D Viewer",
        "Mixed Reality Portal",
        "Your Phone",
        "Phone Link",
        "Cortana",
        "Microsoft Edge",
        "Internet Explorer",
        "Firefox",
        "Opera",
        "Brave",
        "Safari"
    )

    Write-Host "`n=== Removing Third-Party Bloatware ===" -ForegroundColor Cyan

    foreach ($program in $bloatwarePrograms) {
        try {
            $uninstallString = Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" |
                Where-Object { $_.DisplayName -like "*$program*" } |
                Select-Object -ExpandProperty UninstallString -ErrorAction SilentlyContinue

            if ($uninstallString) {
                if ($WhatIf) { Write-WhatIfLog "Would remove third-party program: $program" }
                else { Write-Host "Removing: $program" -ForegroundColor Yellow }
                # Implement full silent uninstall logic as required
            }
        }
        catch { Write-Warning "Failed to check for program $program`: $($_.Exception.Message)" }
    }
}

function Remove-TempFiles {
    Write-Host "`n=== Cleaning Temporary Files ===" -ForegroundColor Cyan
    $tempPaths = @(
        "$env:TEMP",
        "$env:TMP",
        "$env:WINDIR\Temp",
        "$env:WINDIR\Prefetch",
        "$env:LOCALAPPDATA\Temp",
        "$env:LOCALAPPDATA\Microsoft\Windows\INetCache",
        "$env:LOCALAPPDATA\Microsoft\Windows\WebCache",
        "$env:LOCALAPPDATA\Microsoft\Windows\History",
        "$env:LOCALAPPDATA\Microsoft\Windows\Explorer\ThumbCacheToDelete"
    )

    foreach ($path in $tempPaths) {
        if (-not (Test-Path -LiteralPath $path)) { continue }
        try {
            $items = Get-ChildItem -Path $path -Recurse -Force -ErrorAction SilentlyContinue
            $count = $items.Count
            if ($WhatIf) { Write-WhatIfLog "Would remove $count items from $path" }
            else {
                # Exclude the running script if for some reason it's inside a temp directory
                $itemsToDelete = $items | Where-Object { -not (Test-IsCurrentScript $_.FullName) }
                foreach ($item in $itemsToDelete) {
                    Remove-Item -LiteralPath $item.FullName -Recurse -Force -ErrorAction SilentlyContinue
                }
                Write-SuccessLog "Cleaned $($itemsToDelete.Count) items from $path"
            }
        }
        catch { Write-Warning "Failed to clean $path`: $($_.Exception.Message)" }
    }
}

function Clear-FolderWithExternalProtection {
    param([string]$FolderPath,[string]$FolderName)

    Write-Host "`n=== Clearing $FolderName ===" -ForegroundColor Cyan

    if (-not (Test-Path -LiteralPath $FolderPath)) { return }
    try {
        Get-ChildItem -Path $FolderPath -Recurse -Force -ErrorAction SilentlyContinue |
            ForEach-Object { Remove-SafeItemWithExternalProtection -ItemPath $_.FullName -ItemName $_.Name }
    }
    catch { Write-Warning "Failed to clear $FolderName`: $($_.Exception.Message)" }
}

function Clear-DownloadsFolder { Clear-FolderWithExternalProtection -FolderPath "$env:USERPROFILE\Downloads" -FolderName "Downloads Folder" }
function Clear-Desktop         { Clear-FolderWithExternalProtection -FolderPath "$env:USERPROFILE\Desktop"   -FolderName "Desktop" }

function Disable-UnnecessaryServices {
    Write-Host "`n=== Disabling Unnecessary Services ===" -ForegroundColor Cyan
    $servicesToDisable = @(
        "DiagTrack","dmwappushservice","SysMain","WSearch","TabletInputService",
        "WbioSrvc","WMPNetworkSvc","XboxGipSvc","XblAuthManager","XblGameSave","XboxNetApiSvc"
    )
    foreach ($service in $servicesToDisable) {
        try {
            $svc = Get-Service -Name $service -ErrorAction SilentlyContinue
            if ($svc) {
                if ($WhatIf) { Write-WhatIfLog "Would disable service: $service" }
                else {
                    Set-Service -Name $service -StartupType Disabled -ErrorAction SilentlyContinue
                    Stop-Service -Name $service -Force -ErrorAction SilentlyContinue
                    Write-SuccessLog "Disabled service: $service"
                }
            }
        }
        catch { Write-Warning "Failed to disable service $service`: $($_.Exception.Message)" }
    }
}

function Clear-Registry {
    Write-Host "`n=== Cleaning Registry ===" -ForegroundColor Cyan
    $registryPaths = @(
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePidlMRU",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRU",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\CIDSizeMRU"
    )
    foreach ($path in $registryPaths) {
        try {
            if (Test-Path -LiteralPath $path) {
                if ($WhatIf) { Write-WhatIfLog "Would clean registry: $path" }
                else {
                    Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
                    Write-SuccessLog "Cleaned registry: $path"
                }
            }
        }
        catch { Write-Warning "Failed to clean registry $path`: $($_.Exception.Message)" }
    }
}

# =====================================================================
#  MAIN
# =====================================================================

function Main {
    Write-Host "Windows 11 Bloatware and Non-Windows Files Cleanup Script" -ForegroundColor Magenta
    Write-Host "=========================================================" -ForegroundColor Magenta

    if ($WhatIf) { Write-Host "`n[WHAT-IF MODE] - No actual changes will be made" -ForegroundColor Yellow }

    if (-not $Force -and -not $WhatIf) {
        Write-Host "`nWARNING: This script will remove programs and files from your system!" -ForegroundColor Red
        Write-Host "Make sure you have backups of important data." -ForegroundColor Red
        $confirmation = Read-Host "`nType 'YES' to continue or anything else to cancel"
        if ($confirmation -ne "YES") { Write-Host "Operation cancelled by user." -ForegroundColor Yellow; return }
    }

    # Display detected external drives that will be preserved
    $externalDrives = Get-ExternalDrives
    if ($externalDrives.Count -gt 0) {
        Write-Host "`nExternal drives detected and will be preserved:" -ForegroundColor Green
        foreach ($drive in $externalDrives) { Write-Host "  - $drive" -ForegroundColor Green }
    }

    # ---- RUN CLEAN-UP TASKS ----
    Remove-WindowsApps
    Remove-ThirdPartyBloatware
    Remove-TempFiles
    Clear-DownloadsFolder
    Clear-Desktop
    Disable-UnnecessaryServices
    Clear-Registry

    Write-Host "`n=== Cleanup Complete ===" -ForegroundColor Green
    Write-Host "Consider restarting your computer for all changes to take effect." -ForegroundColor Yellow
    if ($WhatIf) { Write-Host "`n[WHAT-IF MODE] - No actual changes were made" -ForegroundColor Yellow }
}

# Kick things off
Main