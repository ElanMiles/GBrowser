#include "discord_rpc.h"

#include <windows.h>

#include <sstream>

namespace gbrowser {

namespace {

struct IpcHeader {
    int32_t opcode;
    int32_t length;
};

std::string pipe_name(int index) {
    std::ostringstream oss;
    oss << "\\\\.\\pipe\\discord-ipc-" << index;
    return oss.str();
}

}

DiscordRPC::DiscordRPC()
    : pipe_handle_(nullptr), connected_(false), nonce_counter_(0) {}

DiscordRPC::~DiscordRPC() {
    disconnect();
}

std::string DiscordRPC::json_escape(const std::string& input) {
    std::string output;
    output.reserve(input.size());
    for (char c : input) {
        switch (c) {
            case '\"': output += "\\\""; break;
            case '\\': output += "\\\\"; break;
            case '\n': output += "\\n"; break;
            case '\r': output += "\\r"; break;
            case '\t': output += "\\t"; break;
            default: output += c; break;
        }
    }
    return output;
}

bool DiscordRPC::write_frame(int opcode, const std::string& payload) {
    if (pipe_handle_ == nullptr) {
        return false;
    }
    HANDLE handle = static_cast<HANDLE>(pipe_handle_);
    IpcHeader header{ opcode, static_cast<int32_t>(payload.size()) };

    DWORD written = 0;
    if (!WriteFile(handle, &header, sizeof(header), &written, nullptr) || written != sizeof(header)) {
        return false;
    }
    if (!payload.empty()) {
        if (!WriteFile(handle, payload.data(), static_cast<DWORD>(payload.size()), &written, nullptr) ||
            written != payload.size()) {
            return false;
        }
    }
    return true;
}

bool DiscordRPC::connect(const std::string& client_id) {
    disconnect();

    for (int i = 0; i < 10; ++i) {
        std::string name = pipe_name(i);
        HANDLE handle = CreateFileA(
            name.c_str(),
            GENERIC_READ | GENERIC_WRITE,
            0,
            nullptr,
            OPEN_EXISTING,
            0,
            nullptr
        );
        if (handle != INVALID_HANDLE_VALUE) {
            pipe_handle_ = handle;
            break;
        }
    }

    if (pipe_handle_ == nullptr) {
        return false;
    }

    std::ostringstream payload;
    payload << "{\"v\":1,\"client_id\":\"" << json_escape(client_id) << "\"}";

    if (!write_frame(0, payload.str())) {
        disconnect();
        return false;
    }

    connected_ = true;
    return true;
}

void DiscordRPC::disconnect() {
    if (pipe_handle_ != nullptr) {
        CloseHandle(static_cast<HANDLE>(pipe_handle_));
        pipe_handle_ = nullptr;
    }
    connected_ = false;
}

bool DiscordRPC::is_connected() const {
    return connected_;
}

std::string DiscordRPC::build_activity_payload(
    const std::string& state,
    const std::string& details,
    long long start_timestamp,
    const std::string& large_image,
    const std::string& large_text,
    const std::string& small_image,
    const std::string& small_text
) {
    nonce_counter_ += 1;

    std::ostringstream oss;
    oss << "{\"cmd\":\"SET_ACTIVITY\",\"args\":{\"pid\":" << GetCurrentProcessId()
        << ",\"activity\":{";
    oss << "\"state\":\"" << json_escape(state) << "\",";
    oss << "\"details\":\"" << json_escape(details) << "\",";
    oss << "\"timestamps\":{\"start\":" << start_timestamp << "},";
    oss << "\"assets\":{";
    oss << "\"large_image\":\"" << json_escape(large_image) << "\",";
    oss << "\"large_text\":\"" << json_escape(large_text) << "\"";
    if (!small_image.empty()) {
        oss << ",\"small_image\":\"" << json_escape(small_image) << "\"";
        oss << ",\"small_text\":\"" << json_escape(small_text) << "\"";
    }
    oss << "}";
    oss << "}},";
    oss << "\"nonce\":\"" << nonce_counter_ << "\"}";

    return oss.str();
}

bool DiscordRPC::update_presence(
    const std::string& state,
    const std::string& details,
    long long start_timestamp,
    const std::string& large_image,
    const std::string& large_text,
    const std::string& small_image,
    const std::string& small_text
) {
    if (!connected_) {
        return false;
    }
    std::string payload = build_activity_payload(
        state, details, start_timestamp, large_image, large_text, small_image, small_text
    );
    return write_frame(1, payload);
}

void DiscordRPC::clear_presence() {
    if (!connected_) {
        return;
    }
    nonce_counter_ += 1;
    std::ostringstream oss;
    oss << "{\"cmd\":\"SET_ACTIVITY\",\"args\":{\"pid\":" << GetCurrentProcessId()
        << ",\"activity\":null},\"nonce\":\"" << nonce_counter_ << "\"}";
    write_frame(1, oss.str());
}

}