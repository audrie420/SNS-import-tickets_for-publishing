# code for API requests related to tags
# contains hardcoded sensitive info

if __name__ == "__main__":
    # Modify sys.path to include the project root directory. accommodates absolute imports from perspective of testrunning module in a subfolder
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from cust_data_API_interactors import header_gen
from cust_data_API_interactors import API_log_entry as ale
import requests


SNS_TAG_IDS = {
    # redacted
}


def __find_login_name(client_name: str):
    # redacted
    return ""


def __is_test(client_name: str):
    # redacted
    return True


def lookup_all_tags_and_taggroups(client_name: str) -> requests.models.Response:
    login_name = __find_login_name(client_name)
    url = f"https://system.spektrix.com/{client_name}/api/v3/tag-groups"
    headers = header_gen.build_headers(
        "GET", login_name, url, None, __is_test(client_name)
    )
    response = requests.get(url, headers=headers)
    response.close()
    return response


def lookup_all_tags(client_name: str) -> requests.models.Response:
    login_name = __find_login_name(client_name)
    url = f"https://system.spektrix.com/{client_name}/api/v3/tags"
    headers = header_gen.build_headers(
        "GET", login_name, url, None, __is_test(client_name)
    )
    response = requests.get(url, headers=headers)
    response.close()
    return response


# add one new tag to customer record
# no api call available to add multiple
def add_tag_to_cust(tag_name: str, cust_id: str, client_name: str) -> requests.models.Response:
    login_name = __find_login_name(client_name)
    url = (
        f"https://system.spektrix.com/{client_name}/api/v3/customers/{cust_id}/tags"
    )
    call = "POST"

    body = {"id": SNS_TAG_IDS[tag_name]}

    headers = header_gen.build_headers(
        call, login_name, url, body, __is_test(client_name)
    )
    response = requests.post(url, headers=headers, json=body)
    ale.log_entry(
        client_name,
        call,
        url,
        response.status_code,
        function_name="add_tags_to_cust",
        body=body,
    )
    response.close()
    return response

class add_tags_ret:
    pass

def add_tags_to_cust(tag_list: str, cust_id: str, client_name: str) -> list[requests.models.Response]:
    func_ret = add_tags_ret()
    func_ret.jsons = []
    func_ret.ok = True
    for tag_name in tag_list:
        response = add_tag_to_cust(tag_name, cust_id, client_name)
        func_ret.jsons.append(response.json())
        if not response.ok:
            func_ret.ok = False
    return func_ret


# https://system.spektrix.com/apitesting/api/v3/Help/Api/GET-v3-customers-id-tags?mode=ShowAll
# show tags of a customer


if __name__ == "__main__":
    from pprint import pprint as pp

    # redacted