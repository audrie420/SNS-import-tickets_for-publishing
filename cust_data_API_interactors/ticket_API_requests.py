# code for API requests that is not used for customer side stuff but for instance/ticket/event side stuff
# contains hardcoded sensitive info

if __name__ == "__main__":
    # Modify sys.path to include the project root directory. accommodates absolute imports from perspective of testrunning module in a subfolder
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from cust_data_API_interactors import header_gen
from cust_data_API_interactors import API_log_entry as ale
import requests
from typing import Optional
from urllib.parse import quote
import inspect


def __find_login_name(client_name: str):
    # redacted
    return ""


def __is_test(client_name: str):
    # redacted
    return True


# create a new basket with customer attached and ticketdelivery set to cobo/will call so that you can confirm basket later
# done tested
def cobo_delivery_create_basket(
    cust_id: str, client_name: str
) -> requests.models.Response:
    login_name = __find_login_name(client_name)
    url = f"https://system.spektrix.com/{client_name}/api/v3/baskets"
    call = "POST"
    body = {"customer": cust_id, "ticketDelivery": {"type": 1}}
    # body = {"customer": cust_id, "ticketDelivery": {"type": 1, "address": {all the lines and stuff}}}
    headers = header_gen.build_headers(
        call, login_name, url, body, __is_test(client_name)
    )
    response = requests.post(url, headers=headers, json=body)
    ale.log_entry(
        client_name,
        call,
        url,
        response.status_code,
        function_name="create_basket",
        body=body,
    )
    response.close()
    return response


# create a new basket with customer attached and ticketdelivery set to agent for testing
# done tested
def agent_delivery_create_basket(
    cust_id: str, client_name: str
) -> requests.models.Response:
    login_name = __find_login_name(client_name)
    url = f"https://system.spektrix.com/{client_name}/api/v3/baskets"
    call = "POST"
    body = {"customer": cust_id, "ticketDelivery": {"type": 3}}
    # body = {"customer": cust_id, "ticketDelivery": {"type": 1, "address": {all the lines and stuff}}}
    headers = header_gen.build_headers(
        call, login_name, url, body, __is_test(client_name)
    )
    response = requests.post(url, headers=headers, json=body)
    ale.log_entry(
        client_name,
        call,
        url,
        response.status_code,
        function_name="create_basket",
        body=body,
    )
    response.close()
    return response


# done tested
# not useful, returns a huge list
def get_all_events(client_name: str) -> requests.models.Response:
    login_name = __find_login_name(client_name)
    url = f"https://system.spektrix.com/{client_name}/api/v3/events"
    headers = header_gen.build_headers(
        "GET", login_name, url, None, __is_test(client_name)
    )
    response = requests.get(url, headers=headers)
    response.close()
    return response


# done tested
# can search by just one instance attribute at a time
# could code in functionality to search by more but thats not necessary
# event name search works on partial match, allows spaces and symbols
# url = f"https://system.spektrix.com/{client_name}/api/v3/instances?startFrom={startDateFrom}&startTo={startDateTo}&eventName={eventName_urlFormat}&attribute_{{name}}={{attributevalue}}&eventattribute_{{name}}={{eventattributevalue}}"
# dates in "YYYY-MM-DD" format
# startfromdate is inclusive, starttodate is not. if you want to search for instance on 2022-02-18, use 2022-02-18 - 2022-02-19 date range
def search_instances_by_multiple_parameters(
    client_name: str,
    startDateFrom: Optional[str] = None,
    startDateTo: Optional[str] = None,
    eventName: Optional[str] = None,
    attributeName: Optional[str] = None,
    attributeValue: Optional[str] = None,
) -> requests.models.Response:
    login_name = __find_login_name(client_name)
    if eventName:
        eventName_urlFormat = quote(eventName)

    url = f"https://system.spektrix.com/{client_name}/api/v3/instances"

    # array of strings to append to url
    appendToUrl = []
    if startDateFrom and startDateTo:
        appendToUrl.append(f"startFrom={startDateFrom}&startTo={startDateTo}")
    if eventName:
        appendToUrl.append(f"eventName={eventName_urlFormat}")
    if attributeName and attributeValue:
        appendToUrl.append(f"attribute_{attributeName}={quote(attributeValue)}")

    n = 0
    for section in appendToUrl:
        if n == 0:
            url += "?"
        else:
            url += "&"
        url += section
        n += 1

    headers = header_gen.build_headers(
        "GET", login_name, url, None, __is_test(client_name)
    )
    response = requests.get(url, headers=headers)
    response.close()
    return response


# done tested
def search_instance_by_AVP_id(
    client_name: str, avp_id: str
) -> requests.models.Response:
    res = search_instances_by_multiple_parameters(
        client_name, attributeName="AVPerformanceCode", attributeValue=avp_id
    )
    return res


# done tested
def lookup_instance_id(client_name: str, instance_id: str) -> requests.models.Response:
    login_name = __find_login_name(client_name)
    url = f"https://system.spektrix.com/{client_name}/api/v3/instances/{instance_id}"
    headers = header_gen.build_headers(
        "GET", login_name, url, None, __is_test(client_name)
    )
    response = requests.get(url, headers=headers)
    response.close()
    return response


# done tested
def lookup_event_id(client_name: str, event_id: str) -> requests.models.Response:
    login_name = __find_login_name(client_name)
    url = f"https://system.spektrix.com/{client_name}/api/v3/events/{event_id}"
    headers = header_gen.build_headers(
        "GET", login_name, url, None, __is_test(client_name)
    )
    response = requests.get(url, headers=headers)
    response.close()
    return response


# done
def lookup_seatplan_id(client_name: str, seatplan_id: str) -> requests.models.Response:
    login_name = __find_login_name(client_name)
    url = f"https://system.spektrix.com/{client_name}/api/v3/plans/{seatplan_id}"
    headers = header_gen.build_headers(
        "GET", login_name, url, None, __is_test(client_name)
    )
    response = requests.get(url, headers=headers)
    response.close()
    return response


# done tested
# very long return list because it iterates through every SEAT in each seatplan too
# seems like deleted seating plans are still accessible by API.
# when you do \codestart\ for seatplan in seatplan_list.json(): pp(seatplan["name"]) \codeend\ the names of old deleted seatplans come up
# returns array of dictionaries. each dictionary is a seatplan.
# each seatplan has the seatplan attributes and a collection of areas (eg balcony, standing area, VIP seating area, middle section, etc)
# and each area has the area attribs and a collection of seats
# and each seat has the seat attribs
def seatplan_list(client_name: str) -> requests.models.Response:
    login_name = __find_login_name(client_name)
    url = f"https://system.spektrix.com/{client_name}/api/v3/plans"
    headers = header_gen.build_headers(
        "GET", login_name, url, None, __is_test(client_name)
    )
    response = requests.get(url, headers=headers)
    response.close()
    return response


# done tested
# provides necessary info to find ticket type
def lookup_pricelist_of_instance(
    client_name: str, instance_id: str
) -> requests.models.Response:
    login_name = __find_login_name(client_name)
    url = f"https://system.spektrix.com/{client_name}/api/v3/instances/{instance_id}/price-list"
    headers = header_gen.build_headers(
        "GET", login_name, url, None, __is_test(client_name)
    )
    response = requests.get(url, headers=headers)
    response.close()
    return response


# done tested
# consider using POST v3/baskets/{id}/tickets/best-available to directly add ticket to basket if that's something you wanna do
def lookup_best_available_seats(
    client_name: str, instance_id: str, quantity: int
) -> requests.models.Response:
    login_name = __find_login_name(client_name)
    url = f"https://system.spektrix.com/{client_name}/api/v3/instances/{instance_id}/best-available?quantity={quantity}"
    headers = header_gen.build_headers(
        "GET", login_name, url, None, __is_test(client_name)
    )
    response = requests.get(url, headers=headers)
    response.close()
    return response

    # # DO NOT USE - incomplete
    # # need to set priceband and seatingarea in body?
    # # idk man i tried without priceband and seating area and it said
    # # "Best Available Seats not possible for this event instance"
    # # whatever just use the GET call instead
    # def put_in_basket_best_avail_seats(
    #     basket_id: str, instance_id: str, quantity: int, client_name: str
    # ) -> requests.models.Response:
    login_name = __find_login_name(client_name)
    url = f"https://system.spektrix.com/{client_name}/api/v3/baskets/{basket_id}/tickets/best-available"
    call = "POST"
    body = {"instance": instance_id, "quantity": quantity}
    # body = {"customer": cust_id, "ticketDelivery": {"type": 1, "address": {all the lines and stuff}}}
    headers = header_gen.build_headers(
        call, login_name, url, body, __is_test(client_name)
    )
    response = requests.post(url, headers=headers, json=body)
    ale.log_entry(
        client_name,
        call,
        url,
        response.status_code,
        function_name=inspect.currentframe().f_code.co_name,
        body=body,
    )
    response.close()
    return response


# done tested
def lookup_basket(client_name: str, basket_id: str) -> requests.models.Response:
    login_name = __find_login_name(client_name)
    url = f"https://system.spektrix.com/{client_name}/api/v3/baskets/{basket_id}"
    headers = header_gen.build_headers(
        "GET", login_name, url, None, __is_test(client_name)
    )
    response = requests.get(url, headers=headers)
    response.close()
    return response


# done tested
# careful, it's possible to checkout a basket with nothing in it. then ur acc has an empty order in spektrix
# can only be used for zero value orders since your API key is system-owner type.
# below is the sample body provided in documentation. but your transactions work with just {"sendConfirmationEmail": False}
# {
#   "sendConfirmationEmail": true,
#   "payWithStoredCardId": "sample string 2",
#   "payWithStoredCardCv2": "sample string 3",
#   "paymentChannel": "Web",
#   "payWithDefaultStoredCard": true,
#   "haveStoredCardId": true
# }
def confirm_basket(
    basket_id: str, send_conf_email: bool, client_name: str
) -> requests.models.Response:
    login_name = __find_login_name(client_name)
    url = (
        f"https://system.spektrix.com/{client_name}/api/v3/baskets/{basket_id}/confirm"
    )
    call = "POST"
    body = {"sendConfirmationEmail": send_conf_email}
    headers = header_gen.build_headers(
        call, login_name, url, body, __is_test(client_name)
    )
    response = requests.post(url, headers=headers, json=body)
    ale.log_entry(
        client_name,
        call,
        url,
        response.status_code,
        function_name="confirm_basket",
        body=body,
    )
    response.close()
    return response


# done tested
def lookup_order_id(client_name: str, order_id: str) -> requests.models.Response:
    login_name = __find_login_name(client_name)
    url = f"https://system.spektrix.com/{client_name}/api/v3/orders/{order_id}"
    headers = header_gen.build_headers(
        "GET", login_name, url, None, __is_test(client_name)
    )
    response = requests.get(url, headers=headers)
    response.close()
    return response


# adds one ticket to basket
# done tested ------ only with one ticket on instance with unreserved seating plan
#     body = [
#         {
#             # redacted
#         }
#     ] # Supply either a seat for reserved areas, or a seating plan for unreserved areas. Do not supply both.
def BASE_API_CALL_add_tickets_to_basket(
    basket_id: str, body: dict, client_name: str
) -> requests.models.Response:
    login_name = __find_login_name(client_name)
    url = (
        f"https://system.spektrix.com/{client_name}/api/v3/baskets/{basket_id}/tickets"
    )
    call = "POST"
    headers = header_gen.build_headers(
        call, login_name, url, body, __is_test(client_name)
    )
    response = requests.post(url, headers=headers, json=body)
    ale.log_entry(
        client_name,
        call,
        url,
        response.status_code,
        function_name="add_tickets_to_basket",
        body=body,
    )
    response.close()
    return response


# only works with unreserved seating plans
def BODY_BUILDER_RECURSIVE_add_tickets_to_basket(
    instance_id: str,
    seat_type_id: str,
    seatplan_id: str,
    existing_body_arr: list = None,
) -> dict:
    if not existing_body_arr:
        body = [
            {
                "instance": instance_id,
                "type": seat_type_id,
                "seatingPlan": seatplan_id,
            }
        ]
        return body
    existing_body_arr.append(
        {"instance": instance_id, "type": seat_type_id, "seatingPlan": seatplan_id}
    )
    return existing_body_arr


if __name__ == "__main__":
    from pprint import pprint as pp

    pp("testing module.....")

    # redacted

    basket = agent_delivery_create_basket(customer_id_sns, client_sns)
    basket_id = basket.json()["id"]

    avpcs = [
        # redacted
    ]
    body = []
    for avpc in avpcs:
        instance_search = search_instance_by_AVP_id(client_sns, avpc)
        instance_id = instance_search.json()[0]["id"]
        event = lookup_event_id(client_sns, instance_search.json()[0]["event"]["id"])
        pp(event.json()["name"])
        pp(instance_search.json()[0]["id"])
        seatplan_id = instance_search.json()[0]["planId"]
        seat_type_search = lookup_pricelist_of_instance(client_sns, instance_id)
        seat_type = seat_type_search.json()["prices"][0]["ticketType"]["id"]
        body = BODY_BUILDER_RECURSIVE_add_tickets_to_basket(
            instance_id, seat_type, seatplan_id, body
        )

    res = BASE_API_CALL_add_tickets_to_basket(basket_id, body, client_sns)
    pp("================ticket added, return below================")
    pp(res.ok)
    pp(res.json())

    end_basket = lookup_basket(client_sns, basket_id)
    pp("================final basket check================")
    pp(end_basket.json())

    # # check out basket
    # checkout = confirm_basket(basket_id, False, client_sns)
    # pp("================checkout function running================")
    # pp(checkout.ok)
    # pp(checkout.json())

    # # # START MIN VIABLE TICKETING FLOW FOR BIG IMPORT! ============================================= #

    # redacted

    # instance_id = instance_search.json()[0]["id"]
    # seatplan_id = instance_search.json()[0]["planId"]

    # seat_type_search = lookup_pricelist_of_instance(client_sns, instance_id)
    # seat_type = seat_type_search.json()["prices"][0]["ticketType"]["id"]
    # body = [
    #     {
    #         "instance": instance_id,
    #         "type": seat_type,  # can find type with GET call for pricelist
    #         "seatingPlan": seatplan_id,
    #     }
    # ]

    # res = add_tickets_to_basket(basket_id, body, client_sns)
    # pp("================ticket added, return below================")
    # pp(res.json())

    # end_basket = lookup_basket(client_sns, basket_id)
    # pp("================final basket check================")
    # pp(end_basket.json())

    # # check out basket
    # checkout = confirm_basket(basket_id, False, client_sns)
    # pp("================checkout function running================")
    # pp(checkout.ok)
    # pp(checkout.json())

    # # # END MIN VIABLE TICKETING FLOW FOR BIG IMPORT! ============================================= #

    # ============================================================

    # # can i lookup next best available seat in an unreserved seating plan?
    # #   weirdly, yes....but cant add ticket with that seat number so its useless probably
    # res = search_instance_by_AVP_id(client_sns, "redacted")
    # pp(res.json())
    # res1 = lookup_best_available_seats(client_sns, res.json()[0]["id"], 3)
    # pp(res1.json())

    # # can i add a ticket with a seat number even though the seating plan is unreserved?
    # # nope, seem like you get "validation failed"

    # basket = create_basket(customer_id_sns, client_sns)
    # basket_id = basket.json()["id"]
    # instance_search = search_instance_by_AVP_id(client_sns, "redacted")
    # instance_id = instance_search.json()[0]["id"]
    # seat_type_search = lookup_pricelist_of_instance(client_sns, instance_id)
    # seat_type = seat_type_search.json()["prices"][0]["ticketType"]["id"]
    # next_best = lookup_best_available_seats(client_sns, instance_id, 1)
    # pp(next_best.json())
    # seat_id = next_best.json()[0]["id"]
    # body = [{"instance": instance_id, "type": seat_type, "seat": seat_id}]
    # res = add_tickets_to_basket(basket_id, body, client_sns)
    # pp(res.json())
    # end_basket = lookup_basket(client_sns, basket_id)
    # pp("final basket check")
    # pp(end_basket.json())

    # ============================================================

    # # passed finding apitesting instance to test tickets on
    # instance_res = search_instances_by_multiple_parameters(client_apitesting, "2025-03-27", "2025-03-28", "Beethoven &")
    # pp(instance_res.ok)
    # # pp(instance_res.json())
    # for instance in instance_res.json():
    #     event_res = lookup_event_id(client_apitesting, instance["event"]["id"])
    #     pp(event_res.json()["name"])
    #     pp(instance)

    # ============================================================
    # passed
    # res = lookup_instance_id(client_sns, "redacted")
    # pp(res.ok)
    # pp(res.json())

    # ============================================================
    # passed
    # res = search_instance_by_AVP_id(client_sns, "redacted")
    # pp(res.ok)
    # pp(res.json())

    # ============================================================
    ## passed basket creation
    # res = create_basket(customer_id_apitesting, client_apitesting)
    # pp(res.ok)
    # pp(res.json())

    # ============================================================
    # QNA / FAQ / notes / whatever

    # can i add a ticket from an instance w reserved seating plan using next best available seat getter (not poster) and then confirm basket?
    #   yes

    # can i add a ticket where the seatplan doesnt match the instance?
    #   dont know, dont care :)

    # can i add a ticket where the seatplan for an instance/event has already been deleted?
    #   dont know, dont care :)

    # seat id returned was 25509 from best available getter. is this necessarily in the correct seating plan?
    # don't know, don't care :)

    # are seat ids only unique across one seating plan?
    #   dont know, don't care :)

    # is there a way i can find out if an instance has a reserved or unreserved seating plan just from api calls?
    #   yes. lookup instance id -> lookup seatplan using planId -> 'type' will say 'Unreserved' if unreserved

    # do all the big import instances have the same unreserved seating plan?
    # no, there are two

    # ============================================================
