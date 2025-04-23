import requests
import logging
import json
import asyncio
import websockets
from .utils import msgbody_build

#  send wbsk api

async def send_by_websocket(params, expect=None, websocket=None):
    try:
        url = params.get('url')
        msg_id = params.get('msgid')
        msg_body = params.get('body')
        retry = params.get('retry')

        ws = websocket or await websockets.connect(url)
    except Exception as e:
        logging.error("[錯誤] WBSK參數解析錯誤: {e}", exc_info= True)

    try:
        msg = msgbody_build(msg_id, msg_body)
        logging.info(f"[SEND] MsgId: {msg_id}")
        await ws.send(json.dumps(msg))
        while True:
            reps = await asyncio.wait_for(ws.recv(), timeout=8)
            jsonify_Reps = json.loads(reps)
            reps_Msgid = jsonify_Reps.get("msgId", 0)
            reps_Msgbody = json.loads(jsonify_Reps.get("msgBody", "{}"))

            #  不需expect or 需expect但回傳值須正確 

            if expect == None or (reps_Msgid == expect[0] and reps_Msgbody['reason'] == expect[1]):
                logging.info(f"[RECV] MsgId: {reps_Msgid} {reps_Msgbody['reason']}")
                return True, reps_Msgbody
            
            #  回傳值不正確且不須retry, 有retry就要等到正確回傳值回來
            if not retry:
                return False, reps_Msgbody
    except asyncio.TimeoutError:
        logging.error(f"[錯誤] 等待MsgId {reps_Msgid} 超時 ")
    except Exception as e:
        logging.error(f"[錯誤] API發送失敗: {e}", exc_info= True)
    return False, None

# parse response

def parse_http_reps(reps):
    reps_status = reps.status_code
    reps_data = json.loads(reps.text)

    return reps_status,reps_data

#  send post

def send_by_post(params, expect):
    try:
        url = params.get("url")
        headers = params.get("headers", {})
        data = params.get("body", {})
        reps = requests.post(url, headers=headers, json=data, timeout=5)
        logging.info(f"[POST] 發送: {url}, data: {data}")

        reps_status, reps_data = parse_http_reps(reps)
        if reps_status != expect[0]:
            return False, reps_data
        
        return True, reps_data['data']
    except Exception as e:
        logging.error(f"[POST] API發送失敗: {e}", exc_info= True)

#  send get

def send_by_get(params, expect):
    try:
        url = params.get("url")
        headers = params.get("headers", {})
        data = params.get("body", {})
        reps = requests.get(url, headers=headers, json=data, timeout=5)
        logging.info(f"[GET] 發送: {url}, data: {data}")

        reps_status, reps_data = parse_http_reps(reps)
        if reps_status != expect[0]:
            return False, reps_data
        
        return True, reps_data['data']

    except Exception as e:
        logging.error(f"[GET] API發送失敗: {e}", exc_info= True)
