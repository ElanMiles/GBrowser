# GBrowser
GBrowser is a Windows desktop web browser built with Python, PySide6, and Chromium through Qt WebEngine.
It combines a custom frameless interface with native Windows integration, including Acrylic and Mica backdrops, rounded window corners, dark title bar support, and Discord Rich Presence.
GBrowser is currently an alpha-stage project.

## Features

### Web Browsing

* Chromium-based web rendering through Qt WebEngine
* Multiple tabs
* Closable and reorderable tabs
* Tab duplication
* Tab muting
* Automatic creation of tabs when a website requests a new window
* Back, forward, reload, and home navigation
* Smart address bar for URLs and search queries
* Loading progress indicator
* HTTPS-aware address bar styling
* JavaScript support
* Local Storage support
* WebGL support
* Browser plugins support through Qt WebEngine
* JavaScript-created windows and tabs
* HTML5 fullscreen support

### Address Bar and Search
The address bar accepts both URLs and search queries.
GBrowser can use:

* Google
* Bing
* DuckDuckGo
* YouTube

The default search engine can be selected in Settings.
The built-in home page also provides a search field with a search-engine selector.

### Tabs
GBrowser provides a custom tab interface with:

* New tabs
* Tab closing
* Tab reordering
* Tab duplication
* Tab muting
* Tab-specific navigation
* Tab-specific zoom
* Context menu actions
* Automatic tab titles
* Automatic URL updates

### Built-in Home Page
GBrowser includes a fully local new-tab page.
The home page contains:

* Live clock
* Current date
* Search box
* Search-engine selector
* Quick-access links
* Animated background effects
* Local HTML/CSS/JavaScript

Quick-access shortcuts include YouTube, Google, GitHub, Reddit, Discord, X/Twitter, Wikipedia, Twitch, and Gmail.
A custom home page URL can also be configured in Settings.

### Find in Page
Press `Ctrl+F` to open the Find in Page bar.
Features include:

* Forward search
* Backward search
* Match feedback
* Visual indication when text is found
* Visual indication when text is not found
* `Escape` to close the search bar and clear the search

### Zoom
Page zoom can be adjusted from 25% to 500%.
Available controls include:

* Zoom in
* Zoom out
* Reset zoom to 100%
* Configurable default zoom

The current zoom level is displayed in the browser title bar.

### Downloads
Web downloads are handled through Qt WebEngine.
Files are automatically placed in the system Downloads directory.
If a file with the same name already exists, GBrowser generates a numbered filename instead of overwriting the existing file.

### Context Menu
The page context menu provides:

* Back
* Forward
* Reload
* Open Link in New Tab
* Copy Link Address
* Copy
* Save Page As
* View Page Source
* Inspect Element
The tab context menu provides:

* Close Tab
* Reload
* Duplicate Tab
* Mute Tab

### Page Source and Developer Tools
GBrowser includes basic developer-oriented browser features.
You can:

* View the current page source in a dedicated source window
* Inspect individual page elements using Chromium's `Inspect Element` action

### Fullscreen
GBrowser supports both browser-level and website-requested fullscreen.
This allows sites such as YouTube to use HTML5 fullscreen video.
When entering fullscreen mode, the browser interface is hidden.

Fullscreen can be toggled with:

`F11`

Pressing `Escape` exits fullscreen or closes the Find in Page bar.

### Windows Integration
GBrowser contains a native C++ module compiled with `pybind11` for Windows-specific functionality.
The native layer provides:

* Windows build detection
* Modern Windows backdrop detection
* Mica
* Acrylic
* Blur effects
* Dark title bar
* Rounded window corners
* Window frame manipulation
* Window shadow support
* Native Discord IPC communication

On supported Windows versions, GBrowser can use the modern system backdrop API.
Windows 11 can use Mica or Acrylic through the native DWM APIs.
Older supported Windows configurations can fall back to Acrylic where available.

### Custom Window Interface
GBrowser uses a frameless window with a custom title bar.
The interface includes:

* Custom navigation controls
* Custom address bar
* Custom minimize, maximize, and close buttons
* Custom tab panel
* Integrated Find button
* Settings button
* Zoom indicator
* Discord connection indicator
* Page loading progress bar
* Custom window dragging
* Double-click title bar maximize/restore behavior

The visual interface is implemented with PySide6 widgets and a custom Qt stylesheet.

### Appearance Settings
GBrowser provides configurable window appearance options.
Available settings include:

* Acrylic transparency
* Backdrop material
* Acrylic
* Mica
* System transparency
* Default zoom level
* Dark theme selection
* Default search engine
* Custom home page

The transparency setting includes a live preview.
The current interface is primarily designed around a dark Windows-style appearance.

### Discord Rich Presence
GBrowser supports Discord Rich Presence through its native Windows IPC implementation.
When enabled, Discord can display information about the current browsing session, including:

* Current website domain
* Current page title
* Browsing start time
* GBrowser application artwork
Discord Rich Presence can be enabled or disabled from Settings.
A custom Discord Client ID can also be supplied.
The browser automatically attempts to reconnect to Discord if the connection is unavailable.
A connection indicator is displayed in the GBrowser title bar.
Discord Desktop must be running for Rich Presence to connect.

### Persistent Settings
GBrowser uses Qt `QSettings` to persist application preferences.
The following settings are stored between launches:

* Acrylic transparency
* Backdrop material
* Theme selection
* Home page
* System transparency
* Default zoom
* Search engine
* Discord Rich Presence state
* Discord Client ID
Browsing sessions, history, and bookmarks are not currently persisted.

## Keyboard Shortcuts

| Shortcut            | Action                                |
| ------------------- | ------------------------------------- |
| `Ctrl+T`            | Open a new tab                        |
| `Ctrl+W`            | Close the current tab                 |
| `Ctrl+R`            | Reload the current page               |
| `F5`                | Reload the current page               |
| `Ctrl+L`            | Focus the address bar                 |
| `Ctrl+F`            | Find in page                          |
| `Ctrl+Home`         | Open the home page                    |
| `Alt+Left`          | Go back                               |
| `Alt+Right`         | Go forward                            |
| `Ctrl+Tab`          | Switch to the next tab                |
| `Ctrl+Shift+Tab`    | Switch to the previous tab            |
| `Ctrl+1` - `Ctrl+8` | Switch to a tab by number             |
| `Ctrl+9`            | Switch to the last tab                |
| `Ctrl++` / `Ctrl+=` | Zoom in                               |
| `Ctrl+-`            | Zoom out                              |
| `Ctrl+0`            | Reset zoom                            |
| `F11`               | Toggle fullscreen                     |
| `Escape`            | Exit fullscreen or close Find in Page |

## Technology

GBrowser is built using:

* Python
* PySide6
* Qt WebEngine
* Chromium
* C++
* pybind11
* CMake
* Windows DWM APIs
* Discord IPC

The Python application provides the browser UI and application logic, while the C++ native module provides Windows-specific functionality and Discord IPC.

## Project Structure
```text
GBrowser/
├── main.py
├── app/
│   ├── __init__.py
│   ├── animations.py
│   ├── browser_view.py
│   ├── discord_rpc_manager.py
│   ├── effects.py
│   ├── find_bar.py
│   ├── icon_button.py
│   ├── settings.py
│   ├── tabs.py
│   ├── tab_panel.py
│   ├── titlebar.py
│   └── window.py
│
├── native/
│   ├── CMakeLists.txt
│   ├── module.cpp
│   ├── effects_win.cpp
│   ├── effects_win.h
│   ├── discord_rpc.cpp
│   └── discord_rpc.h
│
├── ui/
│   ├── home.html
│   └── styles.qss
│
├── gbrowser_native.cp313-win_amd64.pyd
├── LICENSE
└── README.md
```

## Requirements
GBrowser currently targets Windows.
For the native Windows features:

* Windows 10 or Windows 11
* Windows 11 is recommended for Mica and modern backdrop support
* Python 3.13 for development with the included CPython 3.13 native module
* Qt WebEngine through PySide6

The included native module is built for:

```text
Windows x64
CPython 3.13
```

## Running from Source
Install the required Python packages:

```bash
pip install PySide6
```
Then run:

```bash
python main.py
```
The native module must be available in the project directory for native Windows effects and Discord Rich Presence.

## Building the Native Module
The C++ component uses CMake and pybind11.
The native module contains:

* Windows DWM integration
* Windows backdrop support
* Rounded corners
* Dark title bar support
* Acrylic and blur effects
* Discord IPC
* Python bindings through pybind11
The resulting module is:

```text
gbrowser_native.cp313-win_amd64.pyd
```

## Building GBrowser
GBrowser can be packaged with PyInstaller.
A windowed build can be created with:

```bash
pyinstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name GBrowser ^
    --add-data "ui;ui" ^
    --add-binary "gbrowser_native.cp313-win_amd64.pyd;." ^
    --hidden-import "PySide6.QtWebEngineCore" ^
    --hidden-import "PySide6.QtWebEngineWidgets" ^
    --hidden-import "PySide6.QtWebChannel" ^
    main.py
```
The `--windowed` option prevents a console window from appearing.
The `--onefile` option packages the application into a single executable.

## Current Scope
GBrowser is an alpha-stage browser project focused on:

* A custom Windows browser interface
* Chromium-based browsing
* Native Windows visual effects
* Custom tab management
* Basic browser utilities
* Configurable appearance
* Discord Rich Presence

Features such as persistent browsing history, bookmarks, and tab/session restoration are not currently implemented.

## Notes
Adding C++ as a new programming language to Alpha 3 was a very difficult part of the development process.
Because of this, Alpha 3 may be unstable in some areas. There may be issues with the Acrylic effect, including cases where it may not work at all.
File downloads are currently known to be problematic and may cause the browser to crash.
Most of the current issues appeared after C++ was introduced into the project.
I will keep looking into these issues and fix them whenever I find the cause.
I also do not know whether Discord Rich Presence is currently working correctly. I have not had much motivation to test it thoroughly.
Sorry in advance for any inconvenience.
