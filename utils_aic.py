from datetime import datetime


def get_now_par(schedule: list[dict]) -> int:
    d_now = datetime.now()
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


def get_next_par(schedule: list[dict]) -> int:
    d_now = datetime.now()
    for num, item in enumerate(schedule):
        if item['start_hour'] == d_now.hour: # add >
            if item['start_min'] <= d_now.minute:
                return num
            else:
                continue
        if d_now.hour <= item['start_hour']:
            return num
    
    return None