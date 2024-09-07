from loguru import logger
import time
from tinytuya import deviceScan, BulbDevice
from pydantic import BaseModel, validator
import concurrent.futures 
from functools import partial
import asyncio

devices = []
lamps = []

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


def init():

    logger.info("server v0.25 is starting...")

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
        #if d['name'].find('Hall Bulb') != -1:
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

async def dimmer_device(bulb_device, cmd : Command):
    start_time = time.time()

    bulb_device.set_brightness_percentage(cmd.dimmer)
    logger.info(f"Device {devices[bulb_device.address]['name'] } {time.time() - start_time} seconds,dimmer= {cmd.dimmer} " )
    return {"status": "ok"}

def turn_device(bulb_device, cmd : Command):

    start_time = time.time()
    result = None
    if cmd.turn:
        result = bulb_device.turn_on()
        bulb_device.set_brightness_percentage(cmd.dimmer)
        # udp packets can be not reach to the lamps so we repeat calls twice
        result = bulb_device.turn_on()
        bulb_device.set_brightness_percentage(cmd.dimmer)
    else:
        result = bulb_device.turn_off()
        # udp packets can be not reach to the lamps so we repeat calls twice
        result = bulb_device.turn_off()


    if result is not None and 'Err' in result:
        logger.error(f"Error turning on device {devices[bulb_device.address]['name'] }: {result['Error']} - {result['Payload']}")
    else:
        logger.info(f"turned lamp {devices[bulb_device.address]['name'] }:  {time.time() - start_time} seconds, switch = {'on' if cmd.turn else 'off'} with dimmer = {cmd.dimmer} ")


async def turn_devices(cmd: Command, mask):

    i = 0
    t = time.time()

    coros = []
    loop = asyncio.get_event_loop()


    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for lamp in lamps:
            local_cmd = cmd.copy()
            # check mask using lamps
            local_cmd.turn = mask[i]
            coros.append( loop.run_in_executor(pool,partial(turn_device,bulb_device = lamp, cmd = local_cmd)))

            i += 1
        await asyncio.gather(*coros)

    logger.info(f'turn_devices function executed {time.time() - t} sec')


    return {"status": "ok"}
