from datetime import datetime
import logging, os, csv

def getCurrentTime(strf="%Y%m%d%H$M"):
    try:
        return datetime.now().strftime(strf)
    except Exception as e:
        logging.warning(f"時間設定失敗: {e}")
        
def saveReport(filePath, apiName, pa, fa):
    try:
        result="PASS" if fa==0 else "FAIL"
        dir_name = os.path.dirname(filePath)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
        fileExist = os.path.isfile(filePath)

        currTime = getCurrentTime('%Y-%m-%d %H:%M')

        with open(filePath, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not fileExist:
                writer.writerow(["測試時間","API名稱", "PASS數量", "FAIL數量", "測試結果"])
            writer.writerow([currTime, apiName, pa, fa, result])
        logging.info(f"測試檔案: {apiName}, 測試結果:{result}, Pass:{pa}, Fail:{fa}。")
        return f"測試檔案: {apiName}, 測試結果:{result}, Pass:{pa}, Fail:{fa}"
    except Exception as e:
        print(f'儲存測試結果失敗, LOG: {e}')
