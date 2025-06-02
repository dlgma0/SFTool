from datetime import datetime


def get_time_for_logging():
    now = datetime.now()

    # Get current date and time without milliseconds
    return now.strftime("%Y-%m-%d %H:%M:%S")


# V3.0 get formatted date for the Closure Detail used date
def get_current_date():
    today = datetime.today()
    formatted_date = f'[{today.day} {today.strftime("%b %y")}]'
    return  formatted_date

if __name__ == "__main__":
    print(get_time_for_logging())