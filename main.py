from copy import copy
# from fastapi import BackgroundTasks,FastAPI
from fastapi import BackgroundTasks, Depends, FastAPI
from pydantic import BaseModel, validator
from loguru import logger
import uvicorn
import time
from lamp import Command, init, turn_devices, lamps #,day_mask, night_mask
import lamp as l

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    try:
        logger.add(
            "logs/{time:YYYY-MM-DD}.log", 
            enqueue=True, 
            # serialize=True,
            rotation="00:00"
            # format="{time:YYYY-MM-DD HH:mm:ss} | {level} |  {name} | {function} | {line} | {message}",
                )

        init() 

    except Exception as e:
        logger.error(f"Error scanning devices: {e}")


@app.post("/set_mode")
async def set_mode(turn: bool, night_mode:bool):

    logger.info(f"POST request /set_mode?turn={turn}&night_mode={night_mode} ")
    cmd = Command(turn=turn, colourtemp=1000, dimmer=10 if night_mode else 100)
    if night_mode == True:
        # use only the first lamp, other turn off
        mask = [False] * len(lamps)
        if len(lamps) > 0 and turn == True:
            mask[0] = True 

    else:
        # use all lamps
        mask = [True] * len(lamps) if turn == True else [False] * len(lamps)


    res = await turn_devices(cmd, mask)
    # res = await turn_devices(cmd, l.night_mask if night_mode else l.day_mask)
    
    return {"status": "ok"}

@app.post("/set_device")
async def set_device(cmd: Command):
    # Set the status of each device
    mask = [True] * len(lamps)
    res = await turn_devices(cmd,mask)
    
    # udp packets can be not reach to the lamps so we repeat calls twice
    # return await turn_devices(cmd,mask)
    return {"status": "ok"}
    

@app.post("/rescan")
async def rescan():
    try:
        res = init() 
        return {"result": res}

    except Exception as e:
        err = f"Error scanning devices: {e}"
        logger.error(err)
        return {"result": err}





if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)