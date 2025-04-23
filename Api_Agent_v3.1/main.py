import os, time, logging, argparse, sys, asyncio

#  Setting: logging style

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s ",
    datefmt="%Y-%m-%d %H:%M:%S",
    )
from core.yaml_handler import openYaml, getYamlCaseWay
from core.api_handler import parser_yaml_assign

#  Setting: Default Path

BASE_DIR = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
DEFAULT_CASE_DIR = os.path.join(BASE_DIR, './testcase')
DEFAULT_REPORT_DIR = os.path.join(BASE_DIR, './reports')

#  Setting: CLI Parameter

parser = argparse.ArgumentParser()
parser.add_argument('--yaml', default= DEFAULT_CASE_DIR, help="指定YAML測試檔的路徑")
args = parser.parse_args()

#  Counting the api handle time 

def count_time(func):
    async def wrapper(*args, **kwargs):
        logging.info(f"[開始] {args[0]} 測試開始")
        runTesting = time.perf_counter()
        result = await func(*args, **kwargs)
        stopTesting = time.perf_counter()
        runTime = stopTesting-runTesting
        logging.info(f"[結束] {args[0]} 測試結束, 共花費 {runTime:.3f} 秒\n{'='*100}")
        return None
    return wrapper

#  Send Api

@count_time
async def run_testing(file):
    yamlData = openYaml(os.path.join(DEFAULT_CASE_DIR,file))
    await parser_yaml_assign(yamlData)

#  main: loop case

async def main():
    items = getYamlCaseWay(args.yaml)
    try:
        for index, file in enumerate(items):
            await run_testing(file)
    except Exception as e:
        logging.error(f"loop case Error: {e}\n{'='*100}", exc_info=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"主程式運行錯誤: {e}\n{'='*100}", exc_info=True)
    except KeyboardInterrupt:
        logging.error(f"手動斷開運行\n{'='*100}", exc_info=True)
