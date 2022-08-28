var soundInterval = null;

// get webcams of computer and set them as the options of #camera-select
const cameraSelect = document.getElementById('camera-select');
const microphoneSelect = document.getElementById('microphone-select');

const zoomSlider = document.getElementById('zoom-slider');
const zoomSliderValue = document.getElementById('zoom-slider-value');

const trackingSpeedSlider = document.getElementById('tracking-speed-slider');
const trackingSpeedSliderValue = document.getElementById('tracking-speed-slider-value');

const facePercentageSlider = document.getElementById('face-percentage-slider');
const facePercentageSliderValue = document.getElementById('face-percentage-slider-value');

const startupCheckbox = document.getElementById('run-on-startup');
const flipCheckbox = document.getElementById('flip-video-preview');
var video = document.getElementById('video');

// get the values from localStorage so that we can set the proper user settings
var config = localStorage.getItem('center_stage_app_config');
config = JSON.parse(config)

const setConfig = function () {
    config = {
        startup: startupCheckbox.checked,
        flip: flipCheckbox.checked,
        zoom: zoomSlider.value,
        trackingSpeed: trackingSpeedSlider.value,
        facePercentage: facePercentageSlider.value
    }

    localStorage.setItem('center_stage_app_config', JSON.stringify(config));

    renderConfig();
}

function renderConfig() { 
    if (config) {
        startupCheckbox.checked = config.startup === true;
        flipCheckbox.checked = config.flip === true;

        zoomSlider.value = zoomSliderValue.innerText = config.zoom;
        trackingSpeedSlider.value = trackingSpeedSliderValue.innerText = config.trackingSpeed;

        facePercentageSlider.value = facePercentageSliderValue.innerText = config.facePercentage;
        zoomSliderValue.innerText = config.zoom;
        trackingSpeedSliderValue.innerText = config.trackingSpeed;
        facePercentageSliderValue.innerText = config.facePercentage * 100 + '%';
    }
}

function init() {
    // Get the run of startup value from localStorage and set the checkbox accordingly
    renderConfig()

    // get the devices of the computer and add the options
    navigator.mediaDevices.enumerateDevices().then(function (devices) {
        devices.forEach(function (device) {
            if (device.kind === 'videoinput') {
                var option = document.createElement('option');
                option.value = device.deviceId;
                option.text = device.label || 'camera ' + (cameraSelect.length + 1);
                option.text = option.text.replace(/\s\(.+\)/, '');
                cameraSelect.appendChild(option);
            }
        });
    }).catch(function (error) {
        console.log(error.name + ': ' + error.message);
    });

    // get microphones of computer and set them as the options of #microphone-select
    navigator.mediaDevices.enumerateDevices().then(function (devices) {
        devices.forEach(function (device) {
            if (device.kind === 'audioinput') {
                var option = document.createElement('option');
                option.value = device.deviceId;
                option.text = device.label || 'microphone ' + (microphoneSelect.length + 1);
                // Replace the parts of the string that are parentheses with a colon inside the contained string
                microphoneSelect.appendChild(option);
            }
        });
    }).catch(function (error) {
        console.log(error.name + ': ' + error.message);
    });
}

// using the webcam and microphone, start the video stream and play it in the video element
function run() {
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

        // If flipping is enabled, flip the video element
        if (flipCheckbox.checked) {
            video.classList.add('flip');
        } else {
            video.classList.remove('flip');
        }

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

            document.getElementById('sound-level-value').style.width = Math.round(average) + '%';
            document.getElementById('sound-level-value').style.backgroundColor = 'rgb(' + Math.round(average * 2.55) + ',' + Math.round(255 - average * 2.55) + ',0)';
        };
    }).catch(function (error) {
        console.log(error.name + ': ' + error.message);
    })
}

// anytime the webcam or microphone is updated, restart the preview display
cameraSelect.onchange = function () {
    run();
}

// anytime the microphone is updated, restart the preview display
microphoneSelect.onchange = function () {
    run();
}

// anytime the zoom slider is updated, update the value of #zoom-slider-value
zoomSlider.oninput = function () {
    setConfig();
    zoomSliderValue.innerText = this.value;
}

// anytime the tracking speed slider is updated, update the value of #tracking-speed-slider-value
trackingSpeedSlider.oninput = function () {
    setConfig();
    trackingSpeedSliderValue.innerText = this.value;
}

// anytime the face percentage slider is updated, update the value of #face-percentage-slider-value
facePercentageSlider.oninput = function () {
    setConfig();
    const percent = this.value * 100;
    const rounded = Math.round(percent / 1) * 1;
    facePercentageSliderValue.innerText = rounded + '%';
}

startupCheckbox.onchange = function () {
    setConfig();
}

// anytime the flip checkbox is updated, restart the preview display
flipCheckbox.onchange = function () {
    setConfig();
    run();
}

// when the user clicks the "start" button, start the preview
var startButton = document.getElementById('preview');
startButton.onclick = function () {
    run();
}

// document on ready 
document.onreadystatechange = function () {
    if (document.readyState === 'complete') {
        init();
    }
}

Promise.all([
    faceapi.nets.tinyFaceDetector.loadFromUri('models'),
    faceapi.nets.faceLandmark68Net.loadFromUri('models'),
    faceapi.nets.faceRecognitionNet.loadFromUri('models'),
    faceapi.nets.faceExpressionNet.loadFromUri('models'),
]).then(() => { 
    console.log('Finished loading models');
})

// detect when the video starts playing and start the face detection
video.addEventListener('play', function () {
    setInterval(async () => {
        console.log('Running interval')
        const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks().withFaceExpressions();
        console.log('detections', detections)
        // const resizedDetections = faceapi.resizeResults(detections, displaySize);
        // canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
        // faceapi.draw.drawDetections(canvas, resizedDetections);
        // faceapi.draw.drawFaceLandmarks(canvas, resizedDetections);
        // faceapi.draw.drawFaceExpressions(canvas, resizedDetections);
    } , 100);
});