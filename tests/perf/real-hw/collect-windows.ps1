# Mesures comparables sur un PC réel sous Windows 10/11 (mêmes grandeurs que collect-linux.sh).
# Lancer PowerShell EN ADMINISTRATEUR juste après l'ouverture de session, sans rien ouvrir d'autre :
#   powershell -ExecutionPolicy Bypass -File collect-windows.ps1 > rapport-windows.txt
Start-Sleep -Seconds 120
$os = Get-CimInstance Win32_OperatingSystem
$cpu = (Get-CimInstance Win32_Processor | Select-Object -First 1).Name
$totalMB = [math]::Round($os.TotalVisibleMemorySize / 1024)
# « Disponible » = libre + cache réutilisable : même définition que MemAvailable sous Linux.
$availMB = (Get-Counter '\Memory\Available MBytes').CounterSamples[0].CookedValue
"os=$($os.Caption) $($os.Version)"
"cpu=$cpu"
"ram_totale_mio=$totalMB"
"ram_utilisee_mio=$([math]::Round($totalMB - $availMB))"
"processus=$((Get-Process).Count)"
$c = Get-PSDrive C
"disque_systeme_utilise=$([math]::Round($c.Used / 1GB, 1)) Go"
$boot = Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Diagnostics-Performance/Operational'; Id=100} -MaxEvents 1 -ErrorAction SilentlyContinue
if ($boot) { "demarrage_ms=$(([xml]$boot.ToXml()).Event.EventData.Data | Where-Object Name -eq 'BootTime' | Select-Object -ExpandProperty '#text')" }
else { "demarrage_ms=indisponible (journal de diagnostic vide ou droits administrateur requis)" }
