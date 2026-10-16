// Disposition par défaut du bureau NexOS (Plasma 6, API de script du shell).
// Barre supérieure : menu NexOS · espace · horloge (centre) · espace · zone système.
// Dock flottant en bas, centré, ajusté à son contenu : applications épinglées + fenêtres.

var top = new Panel;
top.location = "top";
top.height = 2 * Math.floor(gridUnit * 1.7 / 2);
top.floating = false;

var menu = top.addWidget("org.kde.plasma.kickoff");
menu.currentConfigGroup = ["General"];
menu.writeConfig("icon", "nexos-start");
menu.writeConfig("favoritesDisplay", "0");      // favoris en grille
menu.writeConfig("applicationsDisplay", "1");   // applications en liste
menu.writeConfig("showActionButtonCaptions", "false");

top.addWidget("org.kde.plasma.panelspacer");
var clock = top.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", "true");
clock.writeConfig("dateDisplayFormat", "BesideTime");
top.addWidget("org.kde.plasma.panelspacer");
top.addWidget("org.kde.plasma.systemtray");

var dock = new Panel;
dock.location = "bottom";
dock.height = 2 * Math.floor(gridUnit * 3.4 / 2);
dock.floating = true;
dock.lengthMode = "fit";
dock.alignment = "center";
dock.hiding = "dodgewindows";

var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", [
    "applications:org.kde.dolphin.desktop",
    "applications:firefox-esr.desktop",
    "applications:org.kde.konsole.desktop",
    "applications:org.nexos.PythonCenter.desktop",
    "applications:org.nexos.Assistant.desktop",
    "applications:org.kde.discover.desktop",
    "applications:systemsettings.desktop"
].join(","));
tasks.writeConfig("showOnlyCurrentDesktop", "false");
tasks.writeConfig("indicateAudioStreams", "true");
dock.addWidget("org.kde.plasma.marginsseparator");
dock.addWidget("org.kde.plasma.trash");

// Fond d'écran NexOS sur tous les bureaux (paquet avec variantes clair/sombre).
var all = desktops();
for (var i = 0; i < all.length; i++) {
    var d = all[i];
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "file:///usr/share/wallpapers/NexOS/");
}
