from datetime import datetime


def get_time_for_logging():
    now = datetime.now()

    # Get current date and time without milliseconds
    return now.strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    print(get_time_for_logging())