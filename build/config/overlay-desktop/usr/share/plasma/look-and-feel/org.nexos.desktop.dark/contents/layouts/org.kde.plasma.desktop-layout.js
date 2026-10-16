// NexOS — disposition « îlot » : une seule barre flottante, centrée, ajustée à son contenu.
// [ menu NexOS ] | applications épinglées et fenêtres | [ zone système ] [ horloge ]
// Pas de barre plein écran (Windows), pas de barre de menus (macOS), pas de panneau KDE.
var island = new Panel;
island.location = "bottom";
island.height = 2 * Math.floor(gridUnit * 3.2 / 2);
island.floating = true;
island.lengthMode = "fit";
island.alignment = "center";
island.hiding = "none";

var menu = island.addWidget("org.kde.plasma.kickoff");
menu.currentConfigGroup = ["General"];
menu.writeConfig("icon", "nexos-start");
menu.writeConfig("favoritesDisplay", "0");
menu.writeConfig("applicationsDisplay", "0");
menu.writeConfig("showActionButtonCaptions", "false");
menu.writeConfig("compactMode", "true");

island.addWidget("org.kde.plasma.marginsseparator");
var tasks = island.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", [
    "applications:org.kde.dolphin.desktop",
    "applications:firefox-esr.desktop",
    "applications:org.kde.konsole.desktop",
    "applications:org.nexos.PythonCenter.desktop",
    "applications:org.nexos.Assistant.desktop",
    "applications:org.nexos.ControlCenter.desktop",
    "applications:org.kde.discover.desktop"
].join(","));
tasks.writeConfig("indicateAudioStreams", "true");
tasks.writeConfig("iconSpacing", "2");
island.addWidget("org.kde.plasma.marginsseparator");
var tray = island.addWidget("org.kde.plasma.systemtray");
var clock = island.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", "true");
clock.writeConfig("dateDisplayFormat", "BelowTime");
clock.writeConfig("dateFormat", "shortDate");

var all = desktops();
for (var i = 0; i < all.length; i++) {
    var d = all[i];
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "file:///usr/share/wallpapers/NexOS/");
}
