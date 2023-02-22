from datetime import datetime, datetime, timedelta


def get_now_par(schedule: list[dict], dt: datetime=None) -> int:
    d_now = datetime.now() if dt is None else dt
    for num, item in enumerate(schedule):
        if item['start_hour'] == d_now.hour: # add >
            if item['start_min'] >= d_now.minute:
                pass
            else:
                continue
        if item ['end_hour'] == d_now.hour:
            if item['end_min'] <= d_now.minute:
                pass
            else:
                continue
        if d_now.hour >= item['start_hour'] and d_now.hour <= item['end_hour']:
            # print(item)
            return num
    
    return None


def get_next_par(schedule: list[dict], dt: datetime=None) -> int:
    d_now = datetime.now() if dt is None else dt
    for num, item in enumerate(schedule):
        if item['start_hour'] == d_now.hour: # add >
            if item['start_min'] <= d_now.minute:
                return num
            else:
                continue
        if d_now.hour <= item['start_hour']:
            return num

    return None


def get_remaining_time(schedules: list[dict], dt: datetime=None) -> timedelta:
    schedule = get_now_par(schedules, dt)
    dt = datetime.now() if dt is None else dt
    dt_para = datetime(dt.year, dt.month, dt.day, schedule.end_hour, schedule.end_min)
    return dt_para-dt


def get_next_para_time(schedules: list[dict], dt: datetime=None) -> timedelta:
    schedule = get_now_par(schedules, dt)
    dt = datetime.now() if dt is None else dt
    dt_para = datetime(dt.year, dt.month, dt.day, schedule.end_hour, schedule.end_min)
    return dt_para-dt
