from datetime import datetime
from zoneinfo import ZoneInfo

def is_recording_time(schedule, now=None):
    """Weekly schedule: days are Mon..Sun names, time strings HH:MM (local timezone)."""
    if not schedule or not schedule.get("enabled",False):
        return True
    tz=schedule.get("timezone","Asia/Kolkata")
    now=now or datetime.now(ZoneInfo(tz))
    days=schedule.get("days",{})
    day=now.strftime("%A").lower()
    ranges=days.get(day,[])
    current=now.strftime("%H:%M")
    for item in ranges:
        start=item.get("start","00:00"); end=item.get("end","23:59")
        if start <= end and start <= current <= end: return True
        # overnight schedule, e.g. 22:00–06:00
        if start > end and (current >= start or current <= end): return True
    return False
