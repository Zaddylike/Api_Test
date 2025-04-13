import websockets
import asyncio
import logging
import json
import base64

# Crypto Password
def encryptPassword(user_id: str, password: str) -> str:
    validate_code = "qazwsx"
    encodedPas = base64.b64encode(password.encode()).decode()
    secondEncode = base64.b64encode((encodedPas + user_id).encode()).decode()
    cryptoPwd = base64.b64encode((secondEncode + validate_code).encode()).decode()
    return cryptoPwd

# 組裝MessageBody
def messageBodyBuild(msg_id: int, msg_body: str) -> str:
    return {
        "msgId": msg_id,
        "msgbody": json.dumps(msg_body)
    }

# Parser Casename, Msgid, Msgbody
def parserCaseParams(caseParams):
    try:
        msg_casename = caseParams['params']['casename']
        msg_id = caseParams['params']['msgId']
        msg_body = caseParams['params']['senddata']
        msg_expect = caseParams['expect']
        return msg_casename, msg_id, msg_body, msg_expect
    except Exception as e:
        logging.warning(f"解析測試參數失敗: {e}。")

# Send wbskApi and Retry
async def sendMsgWait(websocket, casename, sendMessage, expect, timeout=10):
    try:
        logging.info(f"[發送]msgId: {sendMessage['msgId']}，等待msgId: {expect[0]}")
        await websocket.send(json.dumps(sendMessage))
        while True:
            reps = await asyncio.wait_for(websocket.recv(), timeout=timeout)
            json_reps = json.loads(reps)
            reps_msgId = json_reps["msgId"]
            reps_msgBody = json.loads(json_reps["msgBody"])

            # if reps_msgId == expect[0] and reps_msgBody['reason'] == expect[1]:
            if reps_msgId == expect[0] and reps_msgBody['reason'] == expect[1]:
                logging.info(f"[收到]正確MsgId: {reps_msgId}, Action: {casename}, Reason: {reps_msgBody['reason']}")
                return True, reps_msgBody
            elif reps_msgId == expect[0]:
                logging.info(f"[收到]正確MsgId: {reps_msgId}, 但Reason: {reps_msgBody['reason']}")
            # else:
            #     logging.info(f"  [跳過]錯誤msgId: {reps_msgId}, 繼續等待msgId: {expect[0]} ")
            await asyncio.sleep(1)
    except asyncio.TimeoutError:
        logging.error(f"等待 MsgId: {expect[0]} 超時")
    except Exception as e:
        logging.error(f"sendMsgWait發生錯誤: {e} 。", exc_info=True)
    return False, None

# Send wbskApi once
async def sendMsgWait_single(websocket, casename, sendMessage, expect, timeout=20):
    try:
        logging.info(f"[發送]msgId: {sendMessage['msgId']}，等待msgId: {expect[0]}")
        await websocket.send(json.dumps(sendMessage))
        reps = await asyncio.wait_for(websocket.recv(), timeout=timeout)
        json_reps = json.loads(reps)
        reps_msgId = json_reps["msgId"]
        reps_msgBody = json.loads(json_reps["msgBody"])
        # logging.info(reps_msgBody)
        if reps_msgId == expect[0] and reps_msgBody['reason'] == expect[1]:
            logging.info(f"[收到]正確MsgId: {reps_msgId},動作:{casename}, Msg Reason: {reps_msgBody['reason']}")
            return True, reps_msgBody
        elif reps_msgId == expect[0]:
            logging.info(f"[收到]正確MsgId: {reps_msgId}, 但Reason不匹配: {reps_msgBody['reason']}")
        # else:
        #     logging.info(f"  [跳過]錯誤msgId: {reps_msgId}, 繼續等待msgId: {expect[0]} ")
    except asyncio.TimeoutError:
        logging.error(f"等待 MsgId: {expect[0]} 超時")
    except Exception as e:
        logging.error(f"sendMsgWait發生錯誤: {e} ", exc_info=True)
    return False, None
# Parser yaml-file and Send
#{"msgId":2103,"msgBody":"{\"gameID\":1003058,\"amount\":6,\"seat\":0,\"usePlatformCoins\":1}"}
async def parseYamlandSend(yamlParams):
    caseLength = len(yamlParams['case'])
    logging.info(f"Websocket API名稱: {yamlParams['apiname']}")
    logging.info(f"Case數量: {caseLength} 個。\n")
    catch_data = {}
    try:
        async with websockets.connect(yamlParams['url']) as websocket:
            for i in range(caseLength):
                msg_casename, msg_id, msg_body, msg_expect = parserCaseParams(yamlParams['case'][i])
                # 處理登入加密
                if msg_id == 201:
                    try:
                        usr_id = msg_body['userName']
                        usr_pwd = msg_body['password']
                        msg_body['password'] = encryptPassword(usr_id, usr_pwd)
                    except Exception as e:
                        logging.warning(f"加密密碼失敗: {e}, caseName: {msg_casename}")

                msg = messageBodyBuild(msg_id, msg_body)
                match msg_id:
                    # 入座
                    case 208:
                        try:
                            for pos in range(8):
                                msg = messageBodyBuild(msg_id, {"pos": pos})
                                repsStatus, reps_msgBody = await sendMsgWait_single(websocket, msg_casename, msg, msg_expect)
                                if repsStatus:
                                    logging.info(f"已坐下順序為 {pos} 的座位")
                                    break
                                await asyncio.sleep(0.5)
                        except Exception as e:
                            logging.warning(f"座位已滿: {e}, caseName: {msg_casename}", exc_info=True)
                    # 進入房間
                    case 2101:
                        try:
                            reps, reps_msgBody = await sendMsgWait(websocket, msg_casename, msg, msg_expect)
                            if reps:
                                catch_data['game_id'] = reps_msgBody['gameID']
                        except Exception as e:
                            logging.warning(f"API 發送失敗: {e}, caseName: {msg_casename}", exc_info=True)
                    #買入、下注、確認下注、
                    case 2102|2103|2104|2120|2121|2135:
                        try:
                            msg_body['gameID'] = catch_data['game_id']
                            msg = messageBodyBuild(msg_id, msg_body)
                            # logging.info(msg)
                            reps, reps_msgBody = await sendMsgWait(websocket, msg_casename, msg, msg_expect)
                            if not reps:
                                logging.warning(f"WebSockets API 發送失敗，msgId: {msg_id}, caseName: {msg_casename}")
                        except Exception as e:
                            logging.warning(f"{msg_id} 發送失敗: {e}, caseName: {msg_casename}", exc_info=True)
                    case _:
                        try:
                            reps, reps_msgBody = await sendMsgWait(websocket, msg_casename, msg, msg_expect)
                            if not reps:
                                logging.warning(f"WebSockets API 發送失敗, msgId: {msg_id}, caseName: {msg_casename}")
                        except Exception as e:
                            logging.warning(f"API發送失敗: {e}, caseName: {msg_casename}", exc_info=True)
    except Exception as e:
        logging.warning(f"Websocket連線錯誤: {e}", exc_info=True)
