import os, time, logging, argparse, sys, asyncio

# Setting: logging style
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s ",
    datefmt="%Y-%m-%d %H:%M:%S",
    )
from core.yaml_handler import openYaml, getYamlCaseWay
from core.api_handler import parseYmlSendApi
from core.wbskApi_handler import parseYamlandSend
from core.report_handler import saveReport

# Setting: Default Path
BASE_DIR = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
CASE_DEFAULT_DIR = os.path.join(BASE_DIR, './api_case')
REPORT_DIR = os.path.join(BASE_DIR, './reports/defaultReport')

# Setting: CLI Parameter
parser = argparse.ArgumentParser()
parser.add_argument('--case', default= CASE_DEFAULT_DIR, help="指定YAML測試檔的路徑")
parser.add_argument('--output', default= REPORT_DIR, help="測試報告輸出路徑")
args = parser.parse_args()

def main():
    # 判斷case路徑,檔案數量。
    items = getYamlCaseWay(args.case)
    logging.info(f'本次測試檔案列表: {items}')
    logging.info(f'='*100)
    time.sleep(1)
    # 開始讀取case內參數及測試。
    for index, file in enumerate(items):
        runTesting = time.perf_counter()
        yamlData = openYaml(file)
        logging.info(f"測試計時開始")
        if yamlData['method'].upper() == 'WEBSOCKET':
            asyncio.run(parseYamlandSend(yamlData))
        else:
            Pass, Fail = parseYmlSendApi(yamlData)
            saveReport(args.output, items[index], Pass, Fail)
        stopTesting = time.perf_counter()
        runTime = stopTesting-runTesting
        logging.info(f"API Name: {yamlData.get('apiname')} 測試結束, 共花費 {runTime:.3f} 秒。")
        logging.info(f'='*100)

if __name__ == "__main__":
    main()