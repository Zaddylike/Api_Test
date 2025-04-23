import logging, time, json, asyncio, copy, websockets
from datetime import datetime
from .send_handler import send_by_websocket, send_by_post, send_by_get
from .report_handler import save_to_report

SEND_TYPE_LIST={
    'websocket': send_by_websocket,
    'get': send_by_get,
    'post': send_by_post,
}

#  decorator candy

def count_reps_time(func):
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        status, reps = await func(*args, **kwargs)
        end = time.perf_counter()
        return status, reps
    return wrapper

#  add params for shared

def add_shared_params(case_params: dict, shared_data: dict):
    try:
        for k, v in case_params['body'].items():
            if isinstance(v, str) and v.startswith('$'):
                var_name = v[1:]
                if var_name in shared_data:
                    case_params['body'][k] = shared_data[var_name]
                    # logging.info(f"[共享參數]:{shared_data}")
        return case_params
    except Exception as e:
        logging.warning(f"[警告] 新增共享參數錯誤:{e}")

#  combine the response data

def combine_headers(api_name, case_name, status, start, end, i, reps):
    try:
        str_reps = json.dumps(reps, ensure_ascii=False)
    except Exception as e:
        str_reps = str(reps)
    return {
        "apiname": api_name,
        "casename": case_name,
        "status": "pass" if status else "fail",
        "run_time": f"{end - start:.3f}s",
        "loop": i + 1,
        "response": str_reps,
        }

#  send api and judge Api type

@count_reps_time
async def send_api_once(params, expect, method, shared_data):

    send_func = SEND_TYPE_LIST.get(method, None)

    if not send_func:
        raise ValueError(f"[錯誤] 不支援method: {method}, 確認.YAML是否打錯")

    #避免汙染, 動態替換
    
    params_copy = copy.deepcopy(params)
    add_shared_params(params_copy, shared_data)

    if method == "websocket":
        if not shared_data.get("websocket"):
            shared_data["websocket"] = await websockets.connect(params_copy.get("url"), ping_interval=None, ping_timeout=20)
        status, reps = await send_func(params_copy, expect, websocket=shared_data["websocket"])
    else:
        status, reps = send_func(params_copy, expect)

    return status, reps

#  parser case params and assign

async def parser_yaml_assign(yamldata:dict):

    api_name = yamldata.get('apiname', "unknown_name")
    cases = yamldata.get("case", [])
    report_data = []
    shared_data = {}

    for case in cases:
        params = case.get('params', {})
        expect = case.get('expect', [])

        name = params.get('casename', "unknown_case_name")
        method = params.get('method', 'post')
        loop = max(1,params.get('loop', 1))
        keep = params.get('keep')

        # handle loop and send

        for i in range(loop):
            start = time.perf_counter()
            status, reps = await send_api_once(params, expect, method, shared_data)
            end = time.perf_counter()

            if status and keep:
                if isinstance(reps, dict) and (keep in reps):
                    shared_data[keep] = reps[keep]

            today = datetime.today().strftime("%Y%m%d") #%H%M%S
            report_data.append(combine_headers(api_name, name, status, start, end, i, reps))

        report_name = f"{today}_{api_name}_report"
        save_to_report(report_name, ["apiname", "casename", "status", "loop", "response", "run_time"], report_data)
