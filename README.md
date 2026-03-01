# GBrowser

A lightweight, frameless web browser built with Python, PySide6, and Chromium via Qt WebEngine. Designed for Windows with a native acrylic blur effect and a clean dark interface.

---

## Features

**Browsing**
- Tabbed browsing with closable, reorderable tabs
- Custom tab panel with scroll support for many open tabs
- Back, forward, reload, and home navigation
- Smart URL bar — detects URLs vs search queries automatically
- Configurable default search engine: Google, Bing, DuckDuckGo, YouTube
- Full page zoom with Ctrl+Plus / Ctrl+Minus / Ctrl+0
- Right-click context menu with back, forward, reload, open in new tab, copy link, view source, save page, and inspect element

**Home Page**
- Built-in new tab page with a live clock and date
- Integrated search bar with engine switcher
- Quick access tiles for popular sites
- Fully local — no network requests, loads instantly

**Fullscreen Video**
- HTML5 fullscreen API is supported, so YouTube and other video sites work in fullscreen
- The browser chrome (titlebar and tab panel) hides automatically on fullscreen entry
- Press F11 or Escape to exit

**Find in Page**
- Ctrl+F opens the find bar at the bottom of the window
- Forward and backward search with visual match feedback
- Escape closes the bar and clears highlights

**Settings**
- Adjustable acrylic transparency with a live preview slider
- Default zoom level
- Default search engine
- Custom home page URL (leave empty to use the built-in home page)
- Toggle for the system transparency effect

**Window**
- Frameless window with custom titlebar
- Drag to move, double-click to maximize or restore
- Native Windows acrylic blur effect via SetWindowCompositionAttribute
- Loading progress bar beneath the titlebar

---

## Requirements

- Windows 10 or Windows 11 (acrylic effect requires Windows 10 1903 or later)

---

## Project Structure

```
GBrowser/
├── main.py                 Entry point
├── app/
│   ├── __init__.py
│   ├── window.py           Main browser window
│   ├── tabs.py             Tab and page management
│   ├── tab_panel.py        Custom tab strip widget
│   ├── titlebar.py         Custom titlebar with controls and progress bar
│   ├── browser_view.py     QWebEngineView subclass with fullscreen and download handling
│   ├── find_bar.py         Find in page widget
│   ├── settings.py         Settings dialog
│   └── effects.py          Windows acrylic blur via ctypes
└── ui/
    ├── home.html           Built-in home/new tab page
    └── styles.qss          Application stylesheet
```

---

## Keyboard Shortcuts

| Shortcut              | Action                        |
|-----------------------|-------------------------------|
| Ctrl+T                | New tab                       |
| Ctrl+W                | Close current tab             |
| Ctrl+R / F5           | Reload                        |
| Ctrl+L                | Focus URL bar                 |
| Ctrl+F                | Find in page                  |
| Ctrl+Home             | Go to home page               |
| Alt+Left              | Back                          |
| Alt+Right             | Forward                       |
| Ctrl+Tab              | Next tab                      |
| Ctrl+Shift+Tab        | Previous tab                  |
| Ctrl+1 through Ctrl+8 | Switch to tab by number       |
| Ctrl+9                | Switch to last tab            |
| Ctrl+Plus / Ctrl+=    | Zoom in                       |
| Ctrl+Minus            | Zoom out                      |
| Ctrl+0                | Reset zoom                    |
| F11                   | Toggle fullscreen             |
| Escape                | Exit fullscreen or close find |

---

## Notes

- The acrylic effect is Windows-only and may not work on all hardware configurations. The browser functions normally without it.
- For the best visual result, use Windows 11 with the dark system theme enabled.
- All tabs are session-only. There is no persistent history or bookmark storage yet.
