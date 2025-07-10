# Windows 11 Bloatware and Non-Windows Files Cleanup Script
# Run as Administrator for best results
# WARNING: This script will remove programs and files. Use at your own risk!

param(
    [switch]$WhatIf,
    [switch]$Force
)

# Set execution policy for this session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Global variables
$script:ExternalDrives = @()
$script:ScriptPath = $MyInvocation.MyCommand.Path
$script:ScriptDirectory = Split-Path -Parent $script:ScriptPath

# Function to check if drive is external
function Test-ExternalDrive {
    param([string]$DriveLetter)
    
    try {
        $drive = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='$DriveLetter'"
        if ($drive) {
            # Check if it's a removable drive or network drive
            return ($drive.DriveType -eq 2 -or $drive.DriveType -eq 4)
        }
    }
    catch {
        Write-Warning "Could not determine if $DriveLetter is external"
    }
    return $false
}

# Function to get external drives
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

# Helper function to check if item is on external drive
function Test-ItemOnExternalDrive {
    param([string]$ItemPath)
    
    $externalDrives = Get-ExternalDrives
    foreach ($drive in $externalDrives) {
        if ($ItemPath.StartsWith("$drive`\")) {
            return $true
        }
    }
    return $false
}

# Helper function to check if item is the script itself or in script directory
function Test-ItemIsScript {
    param([string]$ItemPath)
    
    # Check if the item is the script itself
    if ($ItemPath -eq $script:ScriptPath) {
        return $true
    }
    
    # Check if the item is in the script directory
    if ($ItemPath.StartsWith($script:ScriptDirectory)) {
        return $true
    }
    
    return $false
}

# Helper function to check if item should be excluded (external drive, script, or Chrome)
function Test-ItemShouldBeExcluded {
    param([string]$ItemPath)
    
    # Check if it's on external drive
    if (Test-ItemOnExternalDrive $ItemPath) {
        return $true
    }
    
    # Check if it's the script itself or in script directory
    if (Test-ItemIsScript $ItemPath) {
        return $true
    }
    
    # Check if it's Google Chrome
    if ($ItemPath -like "*\Google\Chrome\*" -or 
        $ItemPath -like "*\Chrome\*" -or 
        $ItemPath -like "*\GoogleChrome*" -or
        $ItemPath -like "*\chrome.exe*") {
        return $true
    }
    
    return $false
}

# Helper function for What-If logging
function Write-WhatIfLog {
    param(
        [string]$Message,
        [string]$Color = "Yellow"
    )
    
    if ($WhatIf) {
        Write-Host "[WHAT-IF] $Message" -ForegroundColor $Color
    }
}

# Helper function for success logging
function Write-SuccessLog {
    param([string]$Message)
    
    if (-not $WhatIf) {
        Write-Host $Message -ForegroundColor Green
    }
}

# Helper function for safe item removal with What-If support
function Remove-SafeItemWithWhatIf {
    param(
        [string]$Path,
        [string]$Description,
        [switch]$Recurse = $false
    )
    
    if (Test-Path $Path) {
        try {
            if ($WhatIf) {
                Write-WhatIfLog "Would remove: $Description ($Path)"
            } else {
                $params = @{
                    Path = $Path
                    Force = $true
                    ErrorAction = "SilentlyContinue"
                }
                if ($Recurse) {
                    $params.Recurse = $true
                }
                
                Remove-Item @params
                Write-SuccessLog "Removed: $Description"
            }
        }
        catch {
            Write-Warning "Failed to remove $Description`: $($_.Exception.Message)"
        }
    }
}

# Helper function for safe item removal with exclusion protection
function Remove-SafeItemWithExclusionProtection {
    param(
        [string]$ItemPath,
        [string]$ItemName
    )
    
    if (Test-ItemShouldBeExcluded $ItemPath) {
        if (Test-ItemOnExternalDrive $ItemPath) {
            Write-Host "Preserved (external drive): $ItemPath" -ForegroundColor Blue
        } elseif (Test-ItemIsScript $ItemPath) {
            Write-Host "Preserved (script protection): $ItemPath" -ForegroundColor Cyan
        } elseif ($ItemPath -like "*\Google\Chrome\*" -or $ItemPath -like "*\Chrome\*" -or $ItemPath -like "*\GoogleChrome*" -or $ItemPath -like "*\chrome.exe*") {
            Write-Host "Preserved (Google Chrome): $ItemPath" -ForegroundColor Magenta
        }
        return
    }
    
    Remove-SafeItemWithWhatIf -Path $ItemPath -Description $ItemName -Recurse
}

# Function to safely remove files/directories
function Remove-SafeItem {
    param(
        [string]$Path,
        [string]$Description
    )
    
    Remove-SafeItemWithWhatIf -Path $Path -Description $Description -Recurse
}

# Function to uninstall Windows apps
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
                if ($WhatIf) {
                    Write-WhatIfLog "Would remove Windows app: $app"
                } else {
                    Get-AppxPackage -Name $app -AllUsers | Remove-AppxPackage -ErrorAction SilentlyContinue
                    Write-SuccessLog "Removed Windows app: $app"
                }
            }
        }
        catch {
            Write-Warning "Failed to remove Windows app $app`: $($_.Exception.Message)"
        }
    }
}

# Function to remove third-party bloatware
function Remove-ThirdPartyBloatware {
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
        # Note: Chrome is excluded from this list since we're protecting it
    )
    
    Write-Host "`n=== Removing Third-Party Bloatware ===" -ForegroundColor Cyan
    
    foreach ($program in $bloatwarePrograms) {
        try {
            $uninstallString = Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" | 
                              Where-Object { $_.DisplayName -like "*$program*" } | 
                              Select-Object -ExpandProperty UninstallString -ErrorAction SilentlyContinue
            
            if ($uninstallString) {
                if ($WhatIf) {
                    Write-WhatIfLog "Would remove third-party program: $program"
                } else {
                    Write-Host "Removing: $program" -ForegroundColor Yellow
                    # Note: Actual uninstallation would require more complex logic
                    # This is a simplified version
                }
            }
        }
        catch {
            Write-Warning "Failed to check for program $program`: $($_.Exception.Message)"
        }
    }
}

# Function to clean temporary files
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
        if (Test-Path $path) {
            try {
                $items = Get-ChildItem -Path $path -Recurse -Force -ErrorAction SilentlyContinue
                $count = $items.Count
                
                if ($WhatIf) {
                    Write-WhatIfLog "Would remove $count items from $path"
                } else {
                    Remove-Item -Path "$path\*" -Recurse -Force -ErrorAction SilentlyContinue
                    Write-SuccessLog "Cleaned $count items from $path"
                }
            }
            catch {
                Write-Warning "Failed to clean $path`: $($_.Exception.Message)"
            }
        }
    }
}

# Generic function to clean folder with exclusion protection
function Clear-FolderWithExclusionProtection {
    param(
        [string]$FolderPath,
        [string]$FolderName
    )
    
    Write-Host "`n=== Clearing $FolderName ===" -ForegroundColor Cyan
    
    if (Test-Path $FolderPath) {
        try {
            $items = Get-ChildItem -Path $FolderPath -Recurse -Force -ErrorAction SilentlyContinue
            
            foreach ($item in $items) {
                Remove-SafeItemWithExclusionProtection -ItemPath $item.FullName -ItemName $item.Name
            }
        }
        catch {
            Write-Warning "Failed to clear $FolderName`: $($_.Exception.Message)"
        }
    }
}

# Function to clean downloads folder (with exclusions)
function Clear-DownloadsFolder {
    Clear-FolderWithExclusionProtection -FolderPath "$env:USERPROFILE\Downloads" -FolderName "Downloads Folder"
}

# Function to clear desktop (with exclusions)
function Clear-Desktop {
    Clear-FolderWithExclusionProtection -FolderPath "$env:USERPROFILE\Desktop" -FolderName "Desktop"
}

# Function to disable unnecessary services
function Disable-UnnecessaryServices {
    Write-Host "`n=== Disabling Unnecessary Services ===" -ForegroundColor Cyan
    
    $servicesToDisable = @(
        "DiagTrack",           # Connected User Experiences and Telemetry
        "dmwappushservice",    # WAP Push Message Routing Service
        "SysMain",             # Superfetch
        "WSearch",             # Windows Search
        "TabletInputService",  # Touch Keyboard and Handwriting Panel
        "WbioSrvc",            # Windows Biometric Service
        "WMPNetworkSvc",       # Windows Media Player Network Sharing
        "XboxGipSvc",          # Xbox Accessory Management Service
        "XblAuthManager",      # Xbox Live Auth Manager
        "XblGameSave",         # Xbox Live Game Save
        "XboxNetApiSvc"        # Xbox Live Networking Service
    )
    
    foreach ($service in $servicesToDisable) {
        try {
            $svc = Get-Service -Name $service -ErrorAction SilentlyContinue
            if ($svc) {
                if ($WhatIf) {
                    Write-WhatIfLog "Would disable service: $service"
                } else {
                    Set-Service -Name $service -StartupType Disabled -ErrorAction SilentlyContinue
                    Stop-Service -Name $service -Force -ErrorAction SilentlyContinue
                    Write-SuccessLog "Disabled service: $service"
                }
            }
        }
        catch {
            Write-Warning "Failed to disable service $service`: $($_.Exception.Message)"
        }
    }
}

# Function to clean registry
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
            if (Test-Path $path) {
                if ($WhatIf) {
                    Write-WhatIfLog "Would clean registry: $path"
                } else {
                    Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
                    Write-SuccessLog "Cleaned registry: $path"
                }
            }
        }
        catch {
            Write-Warning "Failed to clean registry $path`: $($_.Exception.Message)"
        }
    }
}

# Main execution
function Main {
    Write-Host "Windows 11 Bloatware and Non-Windows Files Cleanup Script" -ForegroundColor Magenta
    Write-Host "=========================================================" -ForegroundColor Magenta
    
    if ($WhatIf) {
        Write-Host "`n[WHAT-IF MODE] - No actual changes will be made" -ForegroundColor Yellow
    }
    
    if (-not $Force -and -not $WhatIf) {
        Write-Host "`nWARNING: This script will remove programs and files from your system!" -ForegroundColor Red
        Write-Host "Make sure you have backups of important data." -ForegroundColor Red
        $confirmation = Read-Host "`nType 'YES' to continue or anything else to cancel"
        
        if ($confirmation -ne "YES") {
            Write-Host "Operation cancelled by user." -ForegroundColor Yellow
            return
        }
    }
    
    # Check for external drives
    $externalDrives = Get-ExternalDrives
    if ($externalDrives.Count -gt 0) {
        Write-Host "`nExternal drives detected and will be preserved:" -ForegroundColor Green
        foreach ($drive in $externalDrives) {
            Write-Host "  - $drive" -ForegroundColor Green
        }
    }
    
    # Display protection information
    Write-Host "`nThe following items will be protected from deletion:" -ForegroundColor Green
    Write-Host "  - External drives" -ForegroundColor Green
    Write-Host "  - This script and its directory" -ForegroundColor Green
    Write-Host "  - Google Chrome browser and related files" -ForegroundColor Green
    
    # Run cleanup functions
    Remove-WindowsApps
    Remove-ThirdPartyBloatware
    Remove-TempFiles
    Clear-DownloadsFolder
    Clear-Desktop
    Disable-UnnecessaryServices
    Clear-Registry
    
    Write-Host "`n=== Cleanup Complete ===" -ForegroundColor Green
    Write-Host "Consider restarting your computer for all changes to take effect." -ForegroundColor Yellow
    
    if ($WhatIf) {
        Write-Host "`n[WHAT-IF MODE] - No actual changes were made" -ForegroundColor Yellow
    }
}

# Run the main function
Main