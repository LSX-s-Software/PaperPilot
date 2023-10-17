GRPC_SERVER = {
    "servicers": [
        "user.urls.grpc_hook",
        "oauth.urls.grpc_hook",
    ],
    "interceptors": [
        "paperpilot_common.middleware.server.trace.TraceMiddleware",
        "paperpilot_common.middleware.server.auth.AuthMiddleware",
    ],
    "maximum_concurrent_rpcs": None,
    # optional, list of key-value pairs to configure the channel.
    # The full list of available channel arguments:
    # https://grpc.github.io/grpc/core/group__grpc__arg__keys.html
    "options": [("grpc.max_receive_message_length", 1024 * 1024 * 100)],
    "async": True,
}
