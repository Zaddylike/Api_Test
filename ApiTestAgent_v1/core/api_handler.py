import websockets
import logging, time, json, requests, websockets, asyncio

logging.basicConfig(level=logging.INFO, format='%(message)s')

#parser HTTP API-yaml and Send
def parseYmlSendApi(yamlParams):
    caseLength = len(yamlParams['case'])
    logging.info(f"Case數量: {len(yamlParams['case'])} 個。\n")
    passNum = 0
    failNum = 0

    for i in range(caseLength):
        try:
            yaml_caseName = yamlParams['case'][i]['params']['casename']
            yaml_sendData = yamlParams['case'][i]['params']['senddata']
            yaml_expect = yamlParams['case'][i]['expect']
        except Exception as e:
            logging.warning(f"Yaml解析錯誤: {e}。")
        try:
            if yamlParams["method"].upper() =="POST":
                repsData = requests.post(yamlParams['url'], headers=yamlParams["headers"], json=yaml_sendData)
            elif yamlParams["method"].upper() =="GET":
                repsData = requests.get(yamlParams['url'], headers=yamlParams["headers"], json=yaml_sendData)
            else:
                logging.warning("此Method目前不支援。")
        except Exception as e:
            logging.warning(f"API發送失敗: {e}。")

        caseResult= assertAPI(repsData, yaml_caseName, yaml_expect, i)

        if caseResult:
            passNum +=1
        else:
            failNum+=1
    return passNum, failNum
            
#Assert HTTP API Result
def assertAPI(repsData, yaml_caseName, yaml_expect, index):
    try:
        jsonRepsData = json.loads(repsData.text)
    except Exception as e:
        logging.warning(f"Response格式錯誤: {e}。")
    try:
        if repsData.status_code == yaml_expect[0] and jsonRepsData['msg'] == yaml_expect[1]:
            logging.info(f"{index}-測試API:{yaml_caseName}, 測試結果:Pass, 測試Log: {repsData.text}\n")
            return True
        else:
            logging.info(f"{index}-測試API:{yaml_caseName}, 測試結果:Fail, 測試Log: {repsData.text}\n")
            return False
    except Exception as e:
        logging.warning(f"Response格式驗證失敗: {e}， Status_code:{jsonRepsData.status_code}。")
