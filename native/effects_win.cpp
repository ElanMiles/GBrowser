#include "effects_win.h"

#include <windows.h>
#include <dwmapi.h>

namespace gbrowser {

namespace {

constexpr int ACCENT_DISABLED = 0;
constexpr int ACCENT_ENABLE_BLURBEHIND = 3;
constexpr int ACCENT_ENABLE_ACRYLICBLURBEHIND = 4;
constexpr int WCA_ACCENT_POLICY = 19;

constexpr int DWMWA_USE_IMMERSIVE_DARK_MODE_NEW = 20;
constexpr int DWMWA_USE_IMMERSIVE_DARK_MODE_OLD = 19;
constexpr int DWMWA_WINDOW_CORNER_PREFERENCE = 33;
constexpr int DWMWA_SYSTEMBACKDROP_TYPE = 38;

struct ACCENT_POLICY {
    int AccentState;
    int AccentFlags;
    unsigned int GradientColor;
    int AnimationId;
};

struct WINDOWCOMPOSITIONATTRIBDATA {
    int Attribute;
    void* Data;
    size_t SizeOfData;
};

using SetWindowCompositionAttributeFn = BOOL(WINAPI*)(HWND, WINDOWCOMPOSITIONATTRIBDATA*);

SetWindowCompositionAttributeFn resolve_set_composition_attribute() {
    static SetWindowCompositionAttributeFn cached = nullptr;
    static bool resolved = false;
    if (!resolved) {
        resolved = true;
        HMODULE user32 = GetModuleHandleW(L"user32.dll");
        if (user32 != nullptr) {
            cached = reinterpret_cast<SetWindowCompositionAttributeFn>(
                GetProcAddress(user32, "SetWindowCompositionAttribute"));
        }
    }
    return cached;
}

bool apply_accent(HWND hwnd, int state, unsigned int color, int flags) {
    auto func = resolve_set_composition_attribute();
    if (func == nullptr) {
        return false;
    }
    ACCENT_POLICY accent{};
    accent.AccentState = state;
    accent.AccentFlags = flags;
    accent.GradientColor = color;
    accent.AnimationId = 0;

    WINDOWCOMPOSITIONATTRIBDATA data{};
    data.Attribute = WCA_ACCENT_POLICY;
    data.Data = &accent;
    data.SizeOfData = sizeof(accent);

    return func(hwnd, &data) != FALSE;
}

struct LocalOsVersionInfo {
    ULONG dwOSVersionInfoSize;
    ULONG dwMajorVersion;
    ULONG dwMinorVersion;
    ULONG dwBuildNumber;
    ULONG dwPlatformId;
    WCHAR szCSDVersion[128];
};

using RtlGetVersionPtr = LONG(WINAPI*)(LocalOsVersionInfo*);

}

bool is_windows_platform() {
    return true;
}

int get_windows_build_number() {
    HMODULE mod = GetModuleHandleW(L"ntdll.dll");
    if (mod == nullptr) {
        return 0;
    }
    auto fn = reinterpret_cast<RtlGetVersionPtr>(GetProcAddress(mod, "RtlGetVersion"));
    if (fn == nullptr) {
        return 0;
    }
    LocalOsVersionInfo info{};
    info.dwOSVersionInfoSize = sizeof(info);
    if (fn(&info) == 0) {
        return static_cast<int>(info.dwBuildNumber);
    }
    return 0;
}

bool supports_modern_backdrop() {
    return get_windows_build_number() >= 22000;
}

bool extend_frame_full(void* hwnd_ptr) {
    HWND hwnd = static_cast<HWND>(hwnd_ptr);
    if (hwnd == nullptr) {
        return false;
    }
    MARGINS margins{ -1, -1, -1, -1 };
    return SUCCEEDED(DwmExtendFrameIntoClientArea(hwnd, &margins));
}

bool set_system_backdrop(void* hwnd_ptr, int backdrop_type) {
    HWND hwnd = static_cast<HWND>(hwnd_ptr);
    if (hwnd == nullptr) {
        return false;
    }
    extend_frame_full(hwnd_ptr);
    HRESULT hr = DwmSetWindowAttribute(hwnd, DWMWA_SYSTEMBACKDROP_TYPE, &backdrop_type, sizeof(backdrop_type));
    return SUCCEEDED(hr);
}

bool set_dark_titlebar(void* hwnd_ptr, bool enabled) {
    HWND hwnd = static_cast<HWND>(hwnd_ptr);
    if (hwnd == nullptr) {
        return false;
    }
    BOOL value = enabled ? TRUE : FALSE;
    HRESULT hr = DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_NEW, &value, sizeof(value));
    if (FAILED(hr)) {
        hr = DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_OLD, &value, sizeof(value));
    }
    return SUCCEEDED(hr);
}

bool enable_acrylic(void* hwnd_ptr, uint32_t color) {
    HWND hwnd = static_cast<HWND>(hwnd_ptr);
    if (hwnd == nullptr) {
        return false;
    }
    return apply_accent(hwnd, ACCENT_ENABLE_ACRYLICBLURBEHIND, color, 2);
}

bool enable_blur_behind(void* hwnd_ptr, uint32_t color) {
    HWND hwnd = static_cast<HWND>(hwnd_ptr);
    if (hwnd == nullptr) {
        return false;
    }
    return apply_accent(hwnd, ACCENT_ENABLE_BLURBEHIND, color, 0);
}

bool enable_mica(void* hwnd_ptr, bool dark) {
    HWND hwnd = static_cast<HWND>(hwnd_ptr);
    if (hwnd == nullptr) {
        return false;
    }
    if (supports_modern_backdrop()) {
        set_dark_titlebar(hwnd_ptr, dark);
        return set_system_backdrop(hwnd_ptr, BACKDROP_MICA);
    }
    uint32_t fallback_color = dark ? 0x66101018u : 0x66F5F5F5u;
    return enable_acrylic(hwnd_ptr, fallback_color);
}

bool remove_backdrop(void* hwnd_ptr) {
    HWND hwnd = static_cast<HWND>(hwnd_ptr);
    if (hwnd == nullptr) {
        return false;
    }
    if (supports_modern_backdrop()) {
        set_system_backdrop(hwnd_ptr, BACKDROP_NONE);
    }
    return apply_accent(hwnd, ACCENT_DISABLED, 0, 0);
}

bool set_rounded_corners(void* hwnd_ptr, int preference) {
    HWND hwnd = static_cast<HWND>(hwnd_ptr);
    if (hwnd == nullptr) {
        return false;
    }
    HRESULT hr = DwmSetWindowAttribute(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, &preference, sizeof(preference));
    return SUCCEEDED(hr);
}

bool set_window_shadow(void* hwnd_ptr, bool enabled) {
    HWND hwnd = static_cast<HWND>(hwnd_ptr);
    if (hwnd == nullptr) {
        return false;
    }
    int m = enabled ? 1 : 0;
    MARGINS margins{ m, m, m, m };
    HRESULT hr = DwmExtendFrameIntoClientArea(hwnd, &margins);
    return SUCCEEDED(hr);
}

}