import yaml, os, logging

#open the yaml file
def openYaml(fileName):
    with open(fileName, "r") as file:
        yamlCase = yaml.safe_load(file)
        return yamlCase
    
#survey case-path type, file or folder
def getYamlCaseWay(PATH):
    if os.path.isdir(PATH):
        items = [
            os.path.join(PATH,f) for f in os.listdir(PATH) if f.endswith(('.yaml','.yml'))
        ]
    elif os.path.isfile(PATH):
        items = [PATH]
    else:
        logging.warning("此路徑找不到合規測試檔案。\n")
    return items
