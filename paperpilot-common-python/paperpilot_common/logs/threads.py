from paperpilot_common.logs.utils import is_api_logger_enabled

LOGGER_THREAD = None

if is_api_logger_enabled():
    import threading

    from paperpilot_common.logs.handler import HandleLogAsync

    LOG_THREAD_NAME = "log_thread"

    already_exists = False

    for t in threading.enumerate():
        if t.name == LOG_THREAD_NAME:
            already_exists = True
            break

    if not already_exists:
        t = HandleLogAsync()
        t.daemon = True
        t.name = LOG_THREAD_NAME
        t.start()
        LOGGER_THREAD = t
