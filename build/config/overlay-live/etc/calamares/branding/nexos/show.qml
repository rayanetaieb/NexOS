import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation {
    id: presentation
    Slide {
        Rectangle { anchors.fill: parent; color: "#14181C" }
        Image { source: "nexos-welcome-dark.png"; width: parent.width * 0.6; fillMode: Image.PreserveAspectFit; anchors.centerIn: parent }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter; anchors.bottom: parent.bottom; anchors.bottomMargin: 30
            text: "Installation de NexOS en cours… Python, outils de développement et assistant IA local vous attendent."
            color: "#FFFFFF"; font.pixelSize: 16; wrapMode: Text.WordWrap; width: parent.width * 0.8; horizontalAlignment: Text.Center
        }
    }
    function onActivate() { }
    function onLeave() { }
}
