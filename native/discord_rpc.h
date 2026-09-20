#pragma once
#include <string>

namespace gbrowser {

class DiscordRPC {
public:
    DiscordRPC();
    ~DiscordRPC();

    bool connect(const std::string& client_id);
    void disconnect();
    bool is_connected() const;

    bool update_presence(
        const std::string& state,
        const std::string& details,
        long long start_timestamp,
        const std::string& large_image,
        const std::string& large_text,
        const std::string& small_image,
        const std::string& small_text
    );

    void clear_presence();

private:
    void* pipe_handle_;
    bool connected_;
    int nonce_counter_;

    bool write_frame(int opcode, const std::string& payload);
    std::string build_activity_payload(
        const std::string& state,
        const std::string& details,
        long long start_timestamp,
        const std::string& large_image,
        const std::string& large_text,
        const std::string& small_image,
        const std::string& small_text
    );
    static std::string json_escape(const std::string& input);
};

}