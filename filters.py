import datetime

def format_datetime(value, format="%d %b %Y %I:%M %p"):
    if value is None:
        return ""
    if isinstance(value, str):
        value = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
    return value.strftime(format)
