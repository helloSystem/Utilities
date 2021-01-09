import QtQuick 2.2
import QtQuick.Controls 2.15
import QtQuick.Window 2.0
import QtGraphicalEffects 1.0
import QtMultimedia 5.15


ApplicationWindow {

    // Instantiate a Python object;
    // see 'qmlRegisterType' in the Python file that is using this qml
    function showWizard() {
        return Qt.createQmlObject("import Service 1.0; Wizard {}",
                                  window, "Wizard");
    }

    // Convoluted replacement for "sleep" function; https://stackoverflow.com/a/34770228
    Component {
        id: delayCallerComponent
        Timer {
        }
    }

    // Convoluted replacement for "sleep" function; https://stackoverflow.com/a/34770228
    function delayCall( interval, callback ) {
        var delayCaller = delayCallerComponent.createObject( null, { "interval": interval } );
        delayCaller.triggered.connect( function () {
            callback();
            delayCaller.destroy();
        } );
        delayCaller.start();
    }

    function smoothDisappear() {
        skipButton.opacity = 0;
        welcome.shallContinue = false;
        window.color = "#00000000"; // ARGB fully transparent

        music.volume = 0.3;

        wallpaper.width = window.width;
        wallpaper.height = window.height;
        wallpaper.x = 0;
        wallpaper.y = 0;
        wallpaper.opacity = 1;

        // Convoluted replacement for "sleep" function; https://stackoverflow.com/a/34770228
        delayCall( 15000, function () { music.volume = 0.0; } );
        delayCall( 20000, function () { Qt.quit() } );
    }

    function reset() {
        if (welcome.shallContinue != true) {
            return;
        }
        var welcomeTexts = [
           'Welcome', 'Willkommen', '欢迎', 'Bienvenue', 'Benvenuto', 'Bienvenido', 'ようこそ', 'Mabuhay', 'Välkommen', 'Добро пожаловать', 'Merhaba', 'Bonvenon', '歡迎光臨'
        ];
        var welcomeText = welcomeTexts[Math.floor(Math.random() * welcomeTexts.length)];
        welcome.nextText = welcome.nextText + 1;
        if (welcome.nextText > welcomeTexts.length - 1) {
            smoothDisappear();
            return;
             // welcome.nextText = 0;
        }
        // console.log(welcomeText)
        welcome.text = welcomeTexts[welcome.nextText];
        welcome.x = Screen.width;
        welcome.opacity = 0.5;
        welcomeBlurAnimation.stop();
        welcomeBlur.length = 30;
        welcomeBlurAnimation.start();
        welcomeMovement.start();
    }

    id: window
    visible: true
    visibility: "FullScreen"
    color: "black"

    // NumberAnimation on opacity { to: 1; duration: 1000 }

    SequentialAnimation on color {
        ColorAnimation { to: "grey"; duration: 1000 }
        ColorAnimation { to: "black"; duration: 1000 }
    }

    Component.onDestruction: {
        console.log("Exiting")
    }

    Image{
        id: wallpaper
        source: "/usr/local/share/slim/themes/default/background.jpg"
        width: 0
        height: 0
        // scale: Qt.KeepAspectRatio
        fillMode: Image.PreserveAspectCrop
        clip: true
        x: Screen.width / 2 - width / 2
        y: Screen.height / 2 - height / 2
        opacity: 1;
        Behavior on opacity {
            NumberAnimation {  duration: 3000;
                easing.type: Easing.InCubic;
                onRunningChanged: if (!running) {
                                      console.log("Wallpaper has faded out");
                                      window.visibility = "Hidden";
                                      showWizard();
                                  }
            }
        }

        Behavior on width {
            NumberAnimation {  duration: 2000;
                easing.type: Easing.OutCubic;
                onRunningChanged: if (!running) {
                                      window.opacity = 0;
                                      wallpaper.opacity = 0;
                                  }
            }

        }
        Behavior on height {
            NumberAnimation {  duration: 2000; easing.type: Easing.OutCubic }
        }
        Behavior on x {
            NumberAnimation {  duration: 2000; easing.type: Easing.OutCubic }
        }
        Behavior on y {
            NumberAnimation {  duration: 2000; easing.type: Easing.OutCubic }
        }
    }

    Audio {
        // Could probably play video just as well...
        id: music
        autoPlay: true
        // loops: Audio.Infinite;
        source: "pamgaea-by-kevin-macleod-from-filmmusic-io.mp3"
        volume: 1.0
        Behavior on volume {
            NumberAnimation {  duration: 5000; easing.type: Easing.OutCubic }
        }
    }

    Item {

        Text {
            id: welcome
            renderType: Text.NativeRendering
            text: "Welcome"
            font.family: "Nimbus Sans"
            font.pixelSize: Screen.height / 8
            color: "white"
            property int nextText // Allow a custom property
            nextText: 0
            property bool shallContinue // Allow a custom property
            shallContinue: true
            x: Screen.width
            y: Screen.height / 2 - height / 2
            opacity: 1

            Behavior on opacity {
                NumberAnimation { duration: 3000; easing.type: Easing.OutCubic }
            }

            SequentialAnimation on x {
                id: welcomeMovement
                NumberAnimation { to: Screen.width / 2 - welcome.width / 2; duration: 1500; easing.type: Easing.OutQuad; }
                NumberAnimation { to: 0 - welcome.width; duration: 1500; easing.type: Easing.InQuad; }
                onRunningChanged: if (!running) reset();
            }
        }

        DirectionalBlur {
            id: welcomeBlur
        	anchors.fill: welcome
        	source: welcome
        	samples: 30
        	length: 30
        	angle: 90
        	// transparentBorder : true
            SequentialAnimation on length {
                id: welcomeBlurAnimation
                NumberAnimation  { to: 0; duration: 1500; easing.type: Easing.InQuad; }
                NumberAnimation  { to: 30; duration: 1500; easing.type: Easing.OutQuad; }
            }
        }
    }

/*
    Path {
        // Still need to do something with it, like draw it...
        id: helloPath
        startX: 50; startY: 50
        PathSvg { path: "M 26.816767,36.748271 C 43.203424,67.240957 66.474145,0.31812069 55.270041,32.476855 32.265545,98.505836 29.893572,143.91569 29.893572,143.91569 c 0,0 4.58505,-70.596115 33.845596,-70.596115 29.260591,0 -7.777127,69.109905 17.759383,71.339255 C 107.03503,146.88818 149.25942,78.527398 122.65893,77.041175 96.058441,75.554951 85.096643,140.94325 120.74129,143.1726 156.38598,145.40195 207.35821,31.603066 175.96961,28.630598 144.581,25.65813 143.41473,139.457 175.33529,142.42948 c 31.92063,2.97247 85.36058,-115.66477 52.90796,-117.894121 -32.45261,-2.229351 -35.74697,113.798871 -2.23032,114.541991 21.28041,-1.48624 17.21663,-66.50088 44.88117,-65.014637 39.70208,3.309454 20.43206,76.844967 -7.41485,67.623637 -21.30785,-7.62146 -19.59447,-69.101693 7.53806,-67.61545 19.64913,2.562291 33.14886,28.34421 39.03973,9.71025" }
    }

    AnimatedImage {
        id: hello
        source: "hello_variation.svg"
        smooth: true
        x: Screen.width / 2 - width / 2
        y: Screen.height * 0.33 - height / 2
        visible: true
        opacity: 0.0

        SequentialAnimation on opacity {
            OpacityAnimator{to: 1.0 ; duration: 1000}
        }
    }

    ShaderEffect {
        anchors.fill: parent
        property variant source: hello
        property real frequency: 1
        property real amplitude: 0.1
        property real time: 0.0
        NumberAnimation on time {
            from: 0; to: Math.PI*2; duration: 10000; loops: Animation.Infinite
        }
        fragmentShader: "
                        varying highp vec2 qt_TexCoord0;
                        uniform sampler2D source;
                        uniform lowp float qt_Opacity;
                        uniform highp float frequency;
                        uniform highp float amplitude;
                        uniform highp float time;
                        void main() {
                            highp vec2 texCoord = qt_TexCoord0;
                            texCoord.y = amplitude * sin(time * frequency + texCoord.x * 6.283185) + texCoord.y;
                            gl_FragColor = texture2D(source, texCoord) * qt_Opacity;
                        }"
    }

    */

    RoundButton {
        id: skipButton
        text: "   >   "
        x: Screen.width / 2 - width / 2
        y: Screen.height - 100
        onClicked: smoothDisappear()
        background: Rectangle {
            radius: skipButton.radius
            color: "grey"
        }
    }

}


