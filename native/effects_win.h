#pragma once
#include <cstdint>

namespace gbrowser {

constexpr int BACKDROP_AUTO = 0;
constexpr int BACKDROP_NONE = 1;
constexpr int BACKDROP_MICA = 2;
constexpr int BACKDROP_ACRYLIC = 3;
constexpr int BACKDROP_MICA_ALT = 4;

bool is_windows_platform();
int get_windows_build_number();
bool supports_modern_backdrop();

bool extend_frame_full(void* hwnd);
bool set_system_backdrop(void* hwnd, int backdrop_type);

bool enable_acrylic(void* hwnd, uint32_t color);
bool enable_blur_behind(void* hwnd, uint32_t color);
bool enable_mica(void* hwnd, bool dark);
bool remove_backdrop(void* hwnd);

bool set_dark_titlebar(void* hwnd, bool enabled);
bool set_rounded_corners(void* hwnd, int preference);
bool set_window_shadow(void* hwnd, bool enabled);

}