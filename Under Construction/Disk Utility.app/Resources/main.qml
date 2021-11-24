import QtQuick 2.13
import QtQuick.Window 2.13

Window {
    width: 640
    height: 480
    visible: true
    title: qsTr("Hello World")

    Image {
        id: image
        x: 102
        y: 167
        width: 100
        height: 100
        source: "qrc:/qtquickplugin/images/template_image.png"
        fillMode: Image.PreserveAspectFit
    }

    TextEdit {
        id: textEdit
        x: 130
        y: 74
        width: 80
        height: 20
        text: qsTr("Text Edit")
        font.pixelSize: 12
    }

    Row {
        id: row
        x: 347
        y: 48
        width: 200
        height: 400
    }
}
