const { app, BrowserWindow, Tray, Menu } = require('electron');
const path = require('path');

let window;
let isQuiting;
let tray;

app.on('before-quit', function () {
	isQuiting = true;
});

app.on('ready', () => {
	// Make sure that this app starts in the tray.
	tray = new Tray(path.join(__dirname, 'tray.png'));

	tray.setContextMenu(Menu.buildFromTemplate([
		{
			label: 'Show App', click: function () {
				window.show();
			}
		},
		{
			label: 'Quit', click: function () {
				isQuiting = true;
				app.quit();
			}
		}
	]));

	// Create the window
	window = new BrowserWindow({
		width: 850,
		height: 450,
		show: false,
	});

	// Load the index.html of the app	.
	window.loadURL('file://' + __dirname + '/index.html');

	// Close the window when the window is closed but keep the task running
	window.on('close', function (event) {
		if (!isQuiting) {
			event.preventDefault();
			window.hide();
			event.returnValue = false;
		}
	});
});