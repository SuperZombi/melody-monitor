# Melody Monitor for OBS

<img src="https://shields.io/badge/version-v0.1.0-blue">

<img src="github/images/1.png" width="640px">
<img src="github/images/2.png" width="640px">

## Installation
1. Download archive from [Releases](https://github.com/SuperZombi/melody-monitor/releases)
2. Unpack it to a place convenient for you.
3. Run `melody-monitor.exe` (The program will start in the tray).
4. Click `Open in Browser` and copy the link in your browser.
5. Add a new source in OBS (Browser).
6. Paste the copied link into the URL field and adjust the height and width of the element as required.

## Settings
To change settings, create a file `settings.user.json` next to the `melody-monitor.exe`.<br>
You can change these settings now:
```json
{
	"host": "127.0.0.1",
	"port": 8000,
	"interval": 3,
	"theme": "light"
}
```
You don't need to specify all the settings, specify only those that differ from the default.
<hr>

#### Host
Specify `0.0.0.0` if you want to open access to all computers on the local network.
#### Interval
How often the program will call the Windows API to update media data (seconds)
#### Theme
Specify `dark` if you want a dark theme
<hr>


## Changing accent colors
If you want to add custom styling (for example, change accent colors), you need to create a `mods` folder next to the `melody-monitor.exe`.<br>
Then create a file with any name ending in `.css`.<br>
Hint for changing colors:
```css
body {
    --background: rgba(255, 255, 255, 0.8);
    --shadow: 0 0 4px rgba(0, 0, 0, 0.5);
    --title-text-color: black;
    --artist-text-color: #666;
    --progress-bar-color: #007bff;
    --progress-bar-background: #bbb;
}
```
