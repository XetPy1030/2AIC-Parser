from core import aic

import fastapi
from fastapi.responses import JSONResponse
from datetime import datetime

app = fastapi.FastAPI()

Aic = aic.Aic()


def reformat_to_text(schedule: list[dict]):
    text = ''
    for i in schedule:
        # format: time(start_hour:start_min-end_hour:end_min) name cabinet teacher
        # if hour one digit, add 0
        start_hour = str(i['start_hour']) if len(str(i['start_hour'])) == 2 else f"0{i['start_hour']}"
        end_hour = str(i['end_hour']) if len(str(i['end_hour'])) == 2 else f"0{i['end_hour']}"
        start_min = str(i['start_min']) if len(str(i['start_min'])) == 2 else f"0{i['start_min']}"
        end_min = str(i['end_min']) if len(str(i['end_min'])) == 2 else f"0{i['end_min']}"
        text += f"{start_hour}:{start_min}-{end_hour}:{end_min} {i['name']}\n{i['cabinet']} {i['teacher']}\n"

    return text


@app.get("/2aic")
def get_aic(dt: str, name: str):
    dt = datetime.strptime(dt, '%Y-%m-%d').date()
    objs = Aic.get_diary(dt, name)

    return JSONResponse(content={
        'text': reformat_to_text(objs),
        'error': False,
    })


@app.get("/2aic/allowed")
def get_aic_allowed(dt: str):
    dt = datetime.strptime(dt, '%Y-%m-%d').date()
    objs = Aic.get_allowed_objects(dt)

    return JSONResponse(content={
        'text': objs,
        'error': False,
    })


if __name__ == "__main__":
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser()
    host = parser.add_argument('--host', type=str, default='127.0.0.1')
    port = parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)
