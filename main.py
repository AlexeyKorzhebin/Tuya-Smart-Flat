from fastapi import FastAPI
from pydantic import BaseModel, validator
from tinytuya import deviceScan, BulbDevice
from loguru import logger
import uvicorn
import time

app = FastAPI()

lamps = []
devices = []

class Device(BaseModel):
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
        logger.info("server is starting...")

        start_time = time.time()

        global lamps
        global devices
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

        logger.info(f"Found {len(devices)} devices, {len(lamps)} hall lamps on the network within {int(time.time() - start_time)} seconds")
    except Exception as e:
        logger.error(f"Error scanning devices: {e}")

def turn_on_device(bulb_device, temp, dimmer):
    device_name = devices[bulb_device.address]['name'] 
    for i in range(3):
        result = bulb_device.turn_on()
        if result is not None and 'Err' in result:
            logger.warning(f"Error turning on device {device_name}: {result['Error']} - {result['Payload']}")
            if i == 2:
                return {"error": result['Error']}
        else:
            bulb_device.set_brightness_percentage(dimmer)
            logger.info(f"Device {device_name} turned on with temp={temp}, dimmer={dimmer} in {i + 1} attempts" )
            return {"status": "ok"}


def turn_off_device(bulb_device):
    device_name = devices[bulb_device.address]['name'] 
    for i in range(3):
        result = bulb_device.turn_off()
        if result is not None and 'Err' in result:
            logger.warning(f"Error turning off device {device_name}: {result['Error']} - {result['Payload']}")
            if i == 2:
                return {"error": result['Error']}
        else:
            logger.info(f"Device {device_name} turned off in {i + 1} attempts")
            return {"status": "ok"}


def turn_devices(device: Device):
    for lamp in lamps:
        if device.turn:
            turn_on_device(lamp, device.colourtemp, device.dimmer)
        else:
            turn_off_device(lamp)
    return {"status": "ok"}

@app.post("/set_device")
async def set_device(device: Device):
    # Set the status of each device
    res = turn_devices(device)
    
    # udp packets didn't go to the lamps so we repeat calls
    return turn_devices(device)
    

night_mode_data = Device(**{
                        "turn":False,
                        "colourtemp" : 0, 
                        "dimmer" : 0 
                        }
)

day_mode_data = Device(**{
                        "turn":True,
                        "colourtemp" : 0, 
                        "dimmer" : 100 
                        })



@app.post("/set_mode")
async def set_mode(turn: bool, night_mode:bool):

    if night_mode == True:
        
        if turn:
            turn_on_device(night_mode_data)
            turn_on_device(night_mode_data)
        else:
            turn_devices(night_mode_data)
            turn_devices(night_mode_data)
    else:
        # Set the status of each device
        res = turn_devices(day_mode_data)
        res = turn_devices(day_mode_data)
        
    # udp packets didn't go to the lamps so we repeat calls
    return {"status": "ok"}



if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)