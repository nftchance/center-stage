// get webcams of computer and set them as the options of #camera-select
var cameraSelect = document.getElementById('camera-select');

// get the devices of the computer and add the options
navigator.mediaDevices.enumerateDevices().then(function (devices) {
    devices.forEach(function (device) {
        if (device.kind === 'videoinput') {
            var option = document.createElement('option');
            option.value = device.deviceId;
            option.text = device.label || 'camera ' + (cameraSelect.length + 1);
            cameraSelect.appendChild(option);
        }
    }).then(function () {
        cameraSelect.selectedIndex = 0;
    });
}).catch(function (error) {
    console.log(error.name + ': ' + error.message);
});

// get microphones of computer and set them as the options of #microphone-select
var microphoneSelect = document.getElementById('microphone-select');

navigator.mediaDevices.enumerateDevices().then(function (devices) {
    devices.forEach(function (device) {
        if (device.kind === 'audioinput') {
            var option = document.createElement('option');
            option.value = device.deviceId;
            option.text = device.label || 'microphone ' + (microphoneSelect.length + 1);
            microphoneSelect.appendChild(option);
        }
    }).then(function () {
        microphoneSelect.selectedIndex = 0;
    });
}).catch(function (error) {
    console.log(error.name + ': ' + error.message);
});

// using the webcam and microphone, start the video stream and play it in the video element
var video = document.getElementById('video');

var soundInterval = null;

function startPreview() {
    if (soundInterval) clearInterval(soundInterval);

    // get the selected webcam and microphone
    var constraints = {
        video: {
            deviceId: {
                exact: cameraSelect.value
            }
        },
        audio: {
            deviceId: {
                exact: microphoneSelect.value
            }
        }
    };

    navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
        // Display the video
        video.srcObject = stream;
        video.play();

        // Start the sound interval and analyze the incoming sound so that we can display a working microphone
        const audioContext = new AudioContext();
        const analyser = audioContext.createAnalyser();
        const microphone = audioContext.createMediaStreamSource(stream);
        const scriptProcessor = audioContext.createScriptProcessor(2048, 1, 1);

        analyser.smoothingTimeConstant = 0.8;
        analyser.fftSize = 1024;

        microphone.connect(analyser);
        analyser.connect(scriptProcessor);
        scriptProcessor.connect(audioContext.destination);
        
        scriptProcessor.onaudioprocess = function () {
            const array = new Uint8Array(analyser.frequencyBinCount);
            analyser.getByteFrequencyData(array);
            const arraySum = array.reduce((a, value) => a + value, 0);
            const average = arraySum / array.length;

            document.getElementById('sound-level').style.width = Math.round(average) + '%';
            document.getElementById('sound-level').style.backgroundColor = 'rgb(' + Math.round(average * 2.55) + ',' + Math.round(255 - average * 2.55) + ',0)';                                
        };        
    }).catch(function (error) {
        console.log(error.name + ': ' + error.message);
    })
}

// anytime the webcam or microphone is updated, restart the preview display
cameraSelect.onchange = function () {
    startPreview();
}

// anytime the microphone is updated, restart the preview display
microphoneSelect.onchange = function () {
    startPreview();
}

// when the user clicks the "start" button, start the preview
var startButton = document.getElementById('preview');
startButton.onclick = function () {
    startPreview();
}

startPreview()