# group 1 - API interaction handlers

if __name__ == "__main__":
    # Modify sys.path to include the project root directory. accommodates absolute imports from perspective of testrunning module
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from cust_data_API_interactors import keys as k
import hashlib
import base64
import hmac
import datetime
import wsgiref.handlers as wsgi
import codecs
import json

# https://integrate.spektrix.com/docs/authentication


def __http_date_builder():
    d = datetime.datetime.now(datetime.UTC)
    http_date = wsgi.format_date_time(d.timestamp())
    return http_date


def __build_auth_GET(method, login_name, url, http_date, test=True):
    key = k.sandbox
    if not test:
        key = k.sns
    # Construct StringToSign
    string_to_sign = f"{method}\n{url}\n{http_date}"
    # Compute Signature
    secret_key_bytes = base64.b64decode(key)
    string_to_sign_utf8 = string_to_sign.encode("utf-8")
    hmac_sha1 = hmac.new(secret_key_bytes, string_to_sign_utf8, hashlib.sha1).digest()
    signature = base64.b64encode(hmac_sha1).decode("utf-8")
    # Construct Authorization header
    authorization = f"SpektrixAPI3 {login_name}:{signature}"

    return authorization


def __build_auth_nonGET(method, body, login_name, url, http_date, test=True):
    key = k.sandbox
    if not test:
        key = k.sns

    # Construct BodyStringToSign
    body_utf8 = json.dumps(body).encode("utf-8")
    md5_hash = hashlib.md5(body_utf8).digest()
    body_string_to_sign = codecs.encode(md5_hash, "base64").decode("utf-8").strip()

    # Construct StringToSign
    string_to_sign = f"{method}\n{url}\n{http_date}\n{body_string_to_sign}"

    # Compute Signature
    secret_key_bytes = base64.b64decode(key)
    string_to_sign_utf8 = string_to_sign.encode("utf-8")
    hmac_sha1 = hmac.new(secret_key_bytes, string_to_sign_utf8, hashlib.sha1).digest()
    signature = base64.b64encode(hmac_sha1).decode("utf-8")

    # Construct Authorization header
    authorization = f"SpektrixAPI3 {login_name}:{signature}"

    return authorization


def build_headers(method, login_name, url, body=None, test=True):
    http_date = __http_date_builder()
    headers = {
        "Date": http_date,
        "Host": "system.spektrix.com",
    }
    if body:
        headers["Content-Type"] = "application/json"
        headers["Authorization"] = __build_auth_nonGET(
            method, body, login_name, url, http_date, test
        )
    else:
        headers["Authorization"] = __build_auth_GET(
            method, login_name, url, http_date, test
        )
    return headers


# start of testblock boilerplate head

if __name__ == "__main__":
    # redacted for confidentiality
    pass


## CHATGPT request making process
# # Define your custom headers
# headers = {
#     'Authorization': authorization,
#     'Date': date,
#     'Host': host,
#     'Content-Type': 'application/json'  # Assuming JSON body
# }

# # Define your request body
# request_body = {
#     'key1': 'value1',
#     'key2': 'value2'
# }

# # Make the POST request
# response = requests.post('http://example.com/api/endpoint', headers=headers, json=request_body)
