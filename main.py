from copy import copy
from fastapi import FastAPI
from pydantic import BaseModel, validator
from tinytuya import deviceScan, BulbDevice
from loguru import logger
import uvicorn
import time

app = FastAPI()

lamps = []
devices = []

night_mask = []
day_mask = []

class Command(BaseModel):
    turn: bool
    colourtemp: int
    dimmer: int
    
    @validator('colourtemp')
    def temp_must_be_between_0_and_1000(cls, v):
        if v < 0 or v > 1000:
            raise ValueError('colourtemp must be between 0 and 1000')
        return v

    @validator('dimmer')
    def dimmer_must_be_between_0_and_100(cls, v):
        if v < 0 or v > 100:
            raise ValueError('dimmer must be between 0 and 100')
        return v


night_mode_data = Command(**{
                        "turn":False,
                        "colourtemp" : 0, 
                        "dimmer" : 0 
                        }
)

day_mode_data = Command(**{
                        "turn":True,
                        "colourtemp" : 0, 
                        "dimmer" : 100 
                        })



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

def init():

    logger.info("server is starting...")

    start_time = time.time()

    global lamps
    global devices

    global day_mask
    global night_mask

    lamps.clear()
    devices.clear()
    day_mask.clear()
    night_mask.clear()

    devices = deviceScan()

    for dd in devices:
        d = devices[dd]
        if d['name'].find('Hall Bulb') != -1:
            l = BulbDevice(d['id'], d['ip'], d['key'])
            l.set_version(3.3)
            l.set_retry(True)
            l.set_socketPersistent(True)
            l.set_socketNODELAY(True)   
            lamps.append(l)
        # init all elements day_mask True value 
    day_mask = [True]*len(lamps)

        # init all elements night mask False value except with the first 
    night_mask = [False]*len(lamps)
    if len(night_mask) > 0 :  night_mask[0] = True
    
    msg = f"Found {len(devices)} devices, {len(lamps)} hall lamps on the network within {int(time.time() - start_time)} seconds"
    logger.info(msg)
    logger.info(devices)
    logger.info(lamps)

    res = {"msg": msg,
           "lamps": lamps,
           "devices": devices}

    return res

def turn_device(bulb_device, cmd : Command):

    device_name = devices[bulb_device.address]['name'] 
    for i in range(3):
        result = None
        if cmd.turn:
            result = bulb_device.turn_on()
        else:
            result = bulb_device.turn_off()

        if result is not None and 'Err' in result:
            logger.warning(f"Error turning on device {device_name}: {result['Error']} - {result['Payload']}")
            if i == 2:
                return {"error": result['Error']}
        else:
            bulb_device.set_brightness_percentage(cmd.dimmer)
            logger.info(f"Device {device_name} switch = {'on' if cmd.turn else 'off'} with temp = {cmd.colourtemp}, dimmer= {cmd.dimmer} in {i + 1} attempts" )
            return {"status": "ok"}


def turn_devices(cmd: Command, masks):
    i = 0
    for lamp in lamps:
        local_cmd = cmd.copy()
        # check mask using lamps
        local_cmd.turn = cmd.turn and masks[i]
        turn_device(lamp, local_cmd)
        i += 1

    return {"status": "ok"}


@app.post("/set_mode")
async def set_mode(turn: bool, night_mode:bool):

    if night_mode == True:
        # use only the first lamp, other turn off
        cmd = night_mode_data.copy()
        cmd.turn = turn
    else:
        # use all lamps
        cmd = day_mode_data.copy()
        cmd.turn = turn

    # udp packets can be not reach to the lamps so we repeat calls twice
    res = turn_devices(cmd, night_mask if night_mode else day_mask)
    res = turn_devices(cmd, night_mask if night_mode else day_mask)
    
    return {"status": "ok"}

@app.post("/set_device")
async def set_device(cmd: Command):
    # Set the status of each device
    mask = [True] * len(lamps)
    res = turn_devices(cmd,mask)
    
    # udp packets can be not reach to the lamps so we repeat calls twice
    return turn_devices(cmd,mask)
    

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
    uvicorn.run(app, host="0.0.0.0", port=8000)