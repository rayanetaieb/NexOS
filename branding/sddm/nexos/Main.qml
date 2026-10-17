// Écran de connexion NexOS (SDDM, Qt 6). Aucun module externe : QtQuick + Controls de base.
import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

Rectangle {
    id: root
    width: 1920; height: 1080
    color: "#0B1220"
    readonly property color accent: config.accent ? config.accent : "#2E7CF6"
    readonly property color ink: "#E8EEF8"
    readonly property color muted: "#8A9BB8"
    property int userIndex: userModel.lastIndex >= 0 ? userModel.lastIndex : 0
    property string userName: ""
    property string realName: ""
    property int sessionIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
    LayoutMirroring.enabled: Qt.locale().textDirection === Qt.RightToLeft
    LayoutMirroring.childrenInherit: true

    Image {
        anchors.fill: parent
        source: config.background
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
    }

    // Horloge : en haut à gauche, grande et fine (signature NexOS, pas de carte centrée)
    Column {
        anchors { left: parent.left; top: parent.top; leftMargin: root.width * 0.06; topMargin: root.height * 0.08 }
        spacing: 4
        Text {
            id: clock
            color: root.ink; font.pixelSize: Math.round(root.height * 0.11); font.weight: Font.Light
            text: Qt.formatTime(new Date(), "HH:mm")
        }
        Text {
            id: date
            color: root.muted; font.pixelSize: Math.round(root.height * 0.024)
            text: Qt.locale().toString(new Date(), "dddd d MMMM")
        }
        Timer { interval: 1000; running: true; repeat: true
            onTriggered: { clock.text = Qt.formatTime(new Date(), "HH:mm"); date.text = Qt.locale().toString(new Date(), "dddd d MMMM") } }
    }

    // Panneau de connexion : bande verticale translucide à droite
    Rectangle {
        id: panel
        anchors { right: parent.right; top: parent.top; bottom: parent.bottom }
        width: Math.max(420, root.width * 0.28)
        color: "#CC0E1626"
        Rectangle { anchors { left: parent.left; top: parent.top; bottom: parent.bottom } width: 2; color: root.accent; opacity: 0.6 }

        ColumnLayout {
            anchors.centerIn: parent
            width: parent.width * 0.74
            spacing: 18

            Image {
                Layout.alignment: Qt.AlignHCenter
                source: "logo.svg"; sourceSize.width: 84; sourceSize.height: 84
            }
            Text {
                Layout.alignment: Qt.AlignHCenter
                color: root.ink; font.pixelSize: 30; font.weight: Font.DemiBold
                text: root.realName || root.userName
            }
            ListView {
                id: users
                Layout.fillWidth: true; Layout.preferredHeight: 44   // gardée dimensionnée : ses délégués fournissent le nom même masquée
                visible: count > 1
                orientation: ListView.Horizontal; spacing: 8; clip: true
                model: userModel; currentIndex: root.userIndex
                delegate: Button {
                    property string userName: model.name
                    property string realName: model.realName
                    text: model.realName || model.name
                    checkable: true; checked: ListView.isCurrentItem
                    onClicked: { users.currentIndex = index; root.userName = model.name; root.realName = model.realName; password.forceActiveFocus() }
                    palette.button: checked ? root.accent : "#1B2740"; palette.buttonText: root.ink
                }
            }
            TextField {
                id: password
                Layout.fillWidth: true; Layout.preferredHeight: 48
                echoMode: TextInput.Password
                placeholderText: "Mot de passe"
                placeholderTextColor: root.muted
                color: root.ink; font.pixelSize: 18
                focus: true
                background: Rectangle { radius: 12; color: "#14203A"; border.width: password.activeFocus ? 2 : 1
                    border.color: password.activeFocus ? root.accent : "#2A3A5C" }
                Keys.onReturnPressed: root.login()
                Keys.onEnterPressed: root.login()
            }
            Button {
                id: loginButton
                Layout.fillWidth: true; Layout.preferredHeight: 48
                text: "Se connecter"
                onClicked: root.login()
                contentItem: Text { text: loginButton.text; color: "white"; font.pixelSize: 17; font.weight: Font.DemiBold
                    horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                background: Rectangle { radius: 12; color: loginButton.down ? Qt.darker(root.accent, 1.2) : root.accent }
            }
            Text {
                id: message
                Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.Wrap
                color: "#FF7A85"; font.pixelSize: 15; text: ""
            }
            ComboBox {
                id: session
                Layout.fillWidth: true
                model: sessionModel; textRole: "name"; currentIndex: root.sessionIndex
                font.pixelSize: 14
                contentItem: Text { leftPadding: 14; text: session.displayText; color: root.muted; font: session.font
                    verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
                background: Rectangle { implicitHeight: 40; radius: 10; color: "transparent"; border.color: "#2A3A5C" }
            }
        }

        Row {
            anchors { bottom: parent.bottom; horizontalCenter: parent.horizontalCenter; bottomMargin: 36 }
            spacing: 14
            Repeater {
                model: [ { t: "Veille", a: "suspend", ok: sddm.canSuspend },
                         { t: "Redémarrer", a: "reboot", ok: sddm.canReboot },
                         { t: "Éteindre", a: "powerOff", ok: sddm.canPowerOff } ]
                delegate: Button {
                    visible: modelData.ok
                    text: modelData.t
                    flat: true
                    contentItem: Text { text: parent.text; color: root.muted; font.pixelSize: 14 }
                    background: Rectangle { radius: 8; color: parent.hovered ? "#1B2740" : "transparent" }
                    onClicked: sddm[modelData.a]()
                }
            }
        }
    }

    // Utilisateur par défaut : dernier connecté (ou premier), lu directement dans le modèle.
    Repeater {
        model: userModel
        delegate: Item { Component.onCompleted: if (index === root.userIndex) { root.userName = model.name; root.realName = model.realName } }
    }
    // Session : Plasma Wayland par défaut (session de référence de NexOS) ; X11 reste sélectionnable.
    Repeater {
        model: sessionModel
        delegate: Item { Component.onCompleted: if (String(model.file).indexOf("wayland") >= 0 || String(model.name).indexOf("Wayland") >= 0) root.sessionIndex = index }
    }
    Text { visible: userModel.count === 0; anchors { bottom: parent.bottom; left: parent.left; margins: 24 }
        color: root.muted; text: "Aucun compte utilisateur" }

    function login() {
        if (!root.userName) return
        message.text = ""
        sddm.login(root.userName, password.text, session.currentIndex)
    }
    Connections {
        target: sddm
        function onLoginFailed() { message.text = "Mot de passe incorrect"; password.selectAll(); password.forceActiveFocus() }
    }
    Component.onCompleted: password.forceActiveFocus()
}
