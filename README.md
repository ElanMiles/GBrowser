GBrowser is a basic custom web browser implemented in Python using PySide6 and PySide6 WebEngine. It is a frameless, acrylic-style browser for Windows with a tabbed interface and minimal navigation features.

Overview:

* Implements a **custom acrylic blur background** for Windows using ctypes. This may fail silently on unsupported systems.
* Uses a **frameless window** with a custom title bar containing an icon, title, back/forward/reload buttons, new tab button, URL bar, and window control buttons.
* Supports **tabbed browsing** with closable and movable tabs, but tabs are basic `QWebEngineView` instances.
* URL input automatically prepends `https://` if the user does not specify a scheme.
* Window dragging and maximize/restore behavior is manually handled in the title bar mouse events.
* Minimal styling with hardcoded colors and sizes; no themes or user customization.
* No built-in history, bookmarks, or advanced browser features.

Limitations:

* Only tested on Windows 11 for the acrylic blur effect.
* No error handling for invalid URLs or network errors.
* Single font hardcoded to Segoe UI.
* No persistent storage; all tabs are temporary.

Usage:

* Click `+` to open a new tab.
* Use back/forward/reload buttons to navigate.
* Enter a URL and press Enter to load a page.
* Drag the title bar to move the window or double-click to maximize/restore.
* Close a tab with the `x` on the tab.

License:
MIT License

Acknowledgements:

* Built using PySide6 for GUI and PySide6 WebEngine for web content.
* Acrylic effect code adapted from Windows API documentation.
