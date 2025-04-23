import yaml, os

# 讀取 .yaml 檔案
def openYaml(fileName: str):
    with open(fileName, "r", encoding='utf-8') as file:
        yamlCase = yaml.safe_load(file)
        return yamlCase

# 判斷yaml檔案數量

def getYamlCaseWay(path: str):
    if os.path.isdir(path):
        return [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".yaml") or f.endswith(".yml")]
    elif path.endswith(".yaml") or path.endswith(".yml"):
        return [path]
    else:
        raise ValueError("無效的 YAML 路徑")
