import base64, json, logging

# Crypto Password
def encode_pwd(user_id: str, password: str) -> str:
    validate_code = "qazwsx"
    encodedPas = base64.b64encode(password.encode()).decode()
    secondEncode = base64.b64encode((encodedPas + user_id).encode()).decode()
    cryptoPwd = base64.b64encode((secondEncode + validate_code).encode()).decode()
    return cryptoPwd

# combined MessageBody
def msgbody_build(msg_id: int, msg_body: str):
    try:
        str_body = json.dumps(msg_body)
    except Exception as e:
        str_body = str(msg_body)
    return {
        "msgId": msg_id,
        "msgbody": str_body
    }