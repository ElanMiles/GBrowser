#include <pybind11/pybind11.h>

#include "effects_win.h"
#include "discord_rpc.h"

namespace py = pybind11;

PYBIND11_MODULE(gbrowser_native, m) {
    m.doc() = "GBrowser native acceleration module";

    m.attr("BACKDROP_AUTO") = py::int_(gbrowser::BACKDROP_AUTO);
    m.attr("BACKDROP_NONE") = py::int_(gbrowser::BACKDROP_NONE);
    m.attr("BACKDROP_MICA") = py::int_(gbrowser::BACKDROP_MICA);
    m.attr("BACKDROP_ACRYLIC") = py::int_(gbrowser::BACKDROP_ACRYLIC);
    m.attr("BACKDROP_MICA_ALT") = py::int_(gbrowser::BACKDROP_MICA_ALT);

    m.def("is_windows_platform", &gbrowser::is_windows_platform);
    m.def("get_windows_build_number", &gbrowser::get_windows_build_number);
    m.def("supports_modern_backdrop", &gbrowser::supports_modern_backdrop);

    m.def("extend_frame_full", [](std::uintptr_t hwnd) {
        return gbrowser::extend_frame_full(reinterpret_cast<void*>(hwnd));
    });

    m.def("set_system_backdrop", [](std::uintptr_t hwnd, int backdrop_type) {
        return gbrowser::set_system_backdrop(reinterpret_cast<void*>(hwnd), backdrop_type);
    });

    m.def("enable_acrylic", [](std::uintptr_t hwnd, uint32_t color) {
        return gbrowser::enable_acrylic(reinterpret_cast<void*>(hwnd), color);
    });

    m.def("enable_blur_behind", [](std::uintptr_t hwnd, uint32_t color) {
        return gbrowser::enable_blur_behind(reinterpret_cast<void*>(hwnd), color);
    });

    m.def("enable_mica", [](std::uintptr_t hwnd, bool dark) {
        return gbrowser::enable_mica(reinterpret_cast<void*>(hwnd), dark);
    });

    m.def("remove_backdrop", [](std::uintptr_t hwnd) {
        return gbrowser::remove_backdrop(reinterpret_cast<void*>(hwnd));
    });

    m.def("set_dark_titlebar", [](std::uintptr_t hwnd, bool enabled) {
        return gbrowser::set_dark_titlebar(reinterpret_cast<void*>(hwnd), enabled);
    });

    m.def("set_rounded_corners", [](std::uintptr_t hwnd, int preference) {
        return gbrowser::set_rounded_corners(reinterpret_cast<void*>(hwnd), preference);
    });

    m.def("set_window_shadow", [](std::uintptr_t hwnd, bool enabled) {
        return gbrowser::set_window_shadow(reinterpret_cast<void*>(hwnd), enabled);
    });

    py::class_<gbrowser::DiscordRPC>(m, "DiscordRPC")
        .def(py::init<>())
        .def("connect", &gbrowser::DiscordRPC::connect)
        .def("disconnect", &gbrowser::DiscordRPC::disconnect)
        .def("is_connected", &gbrowser::DiscordRPC::is_connected)
        .def("update_presence", &gbrowser::DiscordRPC::update_presence)
        .def("clear_presence", &gbrowser::DiscordRPC::clear_presence);
}