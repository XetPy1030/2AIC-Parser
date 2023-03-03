def parse_part(objs, name_obj, sheet, cur_x, start_y, num_y):
    for y in range(num_y):
        cur_y = y * 2 + 2 + start_y
        obj_time = sheet[cur_y][0]
        obj_name = sheet[cur_y][cur_x]
        obj_cab = sheet[cur_y][cur_x + 1]
        obj_teacher = sheet[cur_y + 1][cur_x]

        if isinstance(obj_time, float) or isinstance(obj_name, float):
            continue

        start_time, end_time = obj_time.split('-')
        start_hour, start_min = map(int, start_time.split(':'))
        end_hour, end_min = map(int, end_time.split(':'))

        data = {
            'name': obj_name,
            'cabinet': obj_cab,
            'teacher': obj_teacher,
            'start_hour': start_hour,
            'start_min': start_min,
            'end_hour': end_hour,
            'end_min': end_min,
        }

        objs[name_obj].append(data)


def standart_parser(sheet: list[list]):
    objs = {}
    for x in range(len(sheet[0]) // 2):
        cur_x = x * 2 + 1
        name_obj = sheet[0][cur_x]
        objs[name_obj] = objs.get(name_obj, [])

        # print(*sheet, sep='\n')

        parse_part(objs, name_obj, sheet, cur_x, 0, 2)
        parse_part(objs, name_obj, sheet, cur_x, 3, 3)
        parse_part(objs, name_obj, sheet, cur_x, 8, 4)

    return objs


def saturday_parser(sheet: list[list]):
    objs = {}
    for x in range(len(sheet[0]) // 2):
        cur_x = x * 2 + 1
        name_obj = sheet[0][cur_x]
        objs[name_obj] = objs.get(name_obj, [])

        parse_part(objs, name_obj, sheet, cur_x, 0, 4)

    return objs
