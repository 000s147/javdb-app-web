from datetime import datetime


def get_now_datetime():
    now = datetime.now()
    formatted = now.strftime("%Y-%m-%d %H:%M:%S")
    return formatted

def show_log(log_text):
    log = f"{get_now_datetime()}: {log_text}"
    print(log)
    return log

