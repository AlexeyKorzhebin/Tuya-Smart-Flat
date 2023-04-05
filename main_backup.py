from fastapi import FastAPI

import tinytuya
import time

import loguru
from loguru import logger

import uvicorn

curr_light_param  = { "brightness" : 0, "colourtemp" : 0}

d = tinytuya.BulbDevice('bf1c4d57e0d6a25b4am9r3', '192.168.1.41', '54b6d5a683b5cab5')
d.set_version(3.3)  # IMPORTANT to set this regardless of version
d.set_socketPersistent(True)  # Optional: Keep socket open for multiple commands

app = FastAPI()

@app.post("/turn")
async def turn_light(turnon:bool,
                    brightness:int| None = None, 
                    colourtemp:int| None = None):
    start_time = time.time()

    setlight(turnon, brightness, colourtemp)

    return {"message": f"Время выполнения программы: {time.time() - start_time} секунд"}

def setlight(turnon, brightness, colourtemp):
    if brightness:
        curr_light_param["brightness"] = brightness

    if colourtemp:
        curr_light_param["colourtemp"] = colourtemp    

    if turnon:
        res = d.turn_on()
    else:
        d.turn_off()

    er = d.set_white(curr_light_param["brightness"], curr_light_param["colourtemp"])
    logger.debug(f"output {er}")

# Set to White - set_white(brightness, colourtemp):
#    colourtemp: Type A devices range = 0-255 and Type B = 0-1000
@app.post("/param")
async def param_light(brightness:int, 
                      colourtemp:int):
    start_time = time.time()

    if brightness:
        curr_light_param["brightness"] = brightness

    if colourtemp:
        curr_light_param["colourtemp"] = colourtemp   

    d.set_white(curr_light_param["brightness"], curr_light_param["colourtemp"])

    return {"message": f"Время выполнения программы: {time.time() - start_time} секунд"}

@app.post("/color")
async def color_light(r:int, 
                      g:int,
                      b:int):
    start_time = time.time()

    d.set_colour(r, g,b)

    return {"message": f"Время выполнения программы: {time.time() - start_time} секунд"}


if __name__ == "__main__":
    logger.add(
        "logs/{time:YYYY-MM-DD}.log", 
        enqueue=True, 
        # serialize=True,
        rotation="00:00"
        # format="{time:YYYY-MM-DD HH:mm:ss} | {level} |  {name} | {function} | {line} | {message}",
    )
    logger.info("server is starting...")
    uvicorn.run(app, host="0.0.0.0", port=8000)