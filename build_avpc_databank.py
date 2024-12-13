import pandas as pd
from datetime import datetime
import os
from cust_data_API_interactors import cust_API_requests as car
from cust_data_API_interactors import ticket_API_requests as tar
import math
from pprint import pprint as pp
import string_cleaner
import sys
from typing import Optional
import time

SNS_TAGS_LIST = [
    # redacted
]


# done tested
def __insert_row_into_dataframe(
    df: pd.DataFrame, new_row: list
) -> None:  # no return value because function modifies dataframe in place
    """
    Inserts values into the next empty row of the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to update.
    new_row (list): The list of values to insert as a new row
    """
    # Determine the next empty row (either existing NaN row or append to end)
    if df.isna().all(axis=1).any():
        next_empty_index = df.index[df.isna().all(axis=1)].min()
    else:
        next_empty_index = len(df)
    # next_empty_index = df.index[df.isna().all(axis=1)].min() if df.isna().all(axis=1).any() else len(df)

    # Insert the values into the DataFrame at the determined index
    df.loc[next_empty_index] = new_row


# done tested
def __receive_and_input_tag_data_through_terminal(
    instance_databank: pd.DataFrame,
) -> None:
    for index, row in instance_databank.iterrows():
        avpc = row["Shortened AVPC"]
        event_name = row["Event Name"]
        instance_dnt = row["Instance date n time"]
        # collect tag values into list
        print(
            f"""
====================================================================
Input between zero and three tags for the instance with AV Performance Code {avpc}.
The name of the event is {event_name}.

The available tags are listed below, the list is accurate as of December 2024.
(If changes have been made please update the objects SNS_TAGS_LIST and SNS_TAG_IDS
because the spelling must be exactly equivalent to the tags on Spektrix.)

{SNS_TAGS_LIST}
===================================================================="""
        )
        input("Press Enter to acknowledge and continue.")

        def __validation_loop_for_one_tag(
            field_input: list, avpc: str, event_name: str, instance_dnt: str
        ) -> Optional[str]:
            print(
                "====================================================================",
                f"{len(field_input)} tags have been registered for instance {avpc} so far.",
                f"The name of the event is {event_name}",
                f"The date and time of this instance is {instance_dnt}",
                "====================================================================",
                sep="\n",
            )
            selected_tag = input(
                "Enter tag name, or press Enter to indicate there are no more tags for this instance: "
            ).strip()
            if selected_tag in SNS_TAGS_LIST:
                return selected_tag
            elif selected_tag == "":
                return None
            else:
                print(
                    "\n",
                    "=======================================================",
                    f"Invalid tag name. Must exactly match one of the following: {SNS_TAGS_LIST}.",
                    "If changes have been made to tags in Spektrix, please update the ",
                    "objects SNS_TAGS_LIST and SNS_TAG_IDS in program and restart import.",
                    sep="\n",
                )
                return __validation_loop_for_one_tag(field_input, avpc)

        field_input = []
        while len(field_input) < 3:
            validated_return = __validation_loop_for_one_tag(
                field_input, avpc, event_name, instance_dnt
            )
            if not validated_return:
                break
            else:
                field_input.append(validated_return)
        print(f"Finished collecting tags for instance {avpc}.")

        # input tag values from list into instance databank
        counter = len(field_input)
        counter1 = 0
        header_list = ["Tag1", "Tag2", "Tag3"]
        while counter > 0:
            instance_databank.loc[
                instance_databank["Shortened AVPC"] == avpc, header_list[counter1]
            ] = field_input[len(field_input) - counter]
            counter -= 1
            counter1 += 1


# done, tested
def __receive_and_input_tag_data_through_csv(instance_databank: pd.DataFrame) -> None:
    print(
        """
======================================================================

To submit tag data, prepare a csv with the following headers: "AVPC", "Tag1", "Tag2", "Tag3"
The csv should have all AVPC codes that have associated tags under the AVPC header, and up to three tags per AVPC code.
Look in folder past_output_files for examples you can use as templates.

The tag name entered in each cell should be exactly capitalised and spelled the same as in Spektrix.
This program will check the inputs against an local list accurate as of December 2024
If changes have been made to the tags in Spektrix, please update the objects SNS_TAGS_LIST and SNS_TAG_IDS
because the spelling must be exactly equivalent to the tags on Spektrix.

======================================================================"""
    )  # program accepts AVPC codes with no tags attached, or omission of AVPC that do not have associated tags
    # maybe should generate SNS_TAGS_LIST and SNS_TAG_IDS based on API calls too - tag group search. future improvement
    tag_bank_filename = input("Enter relative file path of csv that contains tag data:")
    tag_bank_df = pd.read_csv(tag_bank_filename)
    for index, row in tag_bank_df.iterrows():
        row_dict = row.to_dict()
        avpc = row_dict["AVPC"]
        # check that incoming tagged instance is part of import
        if avpc not in instance_databank["Shortened AVPC"].tolist():
            continue
        # collect tag values into list
        field_input = []
        if row_dict["Tag1"] and pd.notna(row_dict["Tag1"]):
            field_input.append(row_dict["Tag1"])
        if row_dict["Tag2"] and pd.notna(row_dict["Tag2"]):
            field_input.append(row_dict["Tag2"])
        if row_dict["Tag3"] and pd.notna(row_dict["Tag3"]):
            field_input.append(row_dict["Tag3"])
        # input tag values into instance databank
        counter = len(field_input)
        counter1 = 0
        header_list = ["Tag1", "Tag2", "Tag3"]
        while counter > 0:
            instance_databank.loc[
                instance_databank["Shortened AVPC"] == avpc, header_list[counter1]
            ] = field_input[len(field_input) - counter]
            counter -= 1
            counter1 += 1


# done not tested
def __put_in_tag_data(instance_databank: pd.DataFrame) -> None:
    # receive input here
    print(
        "Would you prefer to set tags by manually keying them in or submitting a .csv file?"
    )
    selection = str(input("Key in 1 for manual keying, 2 for csv submission: "))
    if selection == "1":
        __receive_and_input_tag_data_through_terminal(instance_databank)

    elif selection == "2":
        __receive_and_input_tag_data_through_csv(instance_databank)
    else:
        print(
            "Error, invalid input. Key in 1 or 2. Program will end now, restart the import process if you wish to continue"
        )
        exit()


# done tested
def databank_builder_and_printer(
    incoming_import_df: pd.DataFrame, client_name: str, INCOMING_TIMESTAMP: float
) -> pd.DataFrame:
    # initialise instance_data_bank
    columns = [
        "Shortened AVPC",
        "Instance ID",
        "Seat Plan ID",
        "Seat Type ID",
        "Seat Type Name",
        "Event Name",
        "Instance date n time",
    ]
    instance_data_bank = pd.DataFrame(columns=columns)

    print(
        "=======================================================================",
        "Gathering necessary ticketing data from the API - please wait about 5 seconds per unique instance being imported",
        "Come back for next input after that time has elapsed.",
        "=======================================================================",
        sep="\n",
    )
    for incoming_short_code in incoming_import_df["Shortened Codes"]:
        incoming_short_code = string_cleaner.clean_text(incoming_short_code)
        if (
            incoming_short_code not in instance_data_bank["Shortened AVPC"].values
        ):  # .values necessary to convert it to array or else comparison doesnt work
            shortened_avpc = incoming_short_code
            instance_search = tar.search_instance_by_AVP_id(client_name, shortened_avpc)

            try:
                instance_id = instance_search.json()[0]["id"]
            except Exception as e:
                print(
                    "Error occurred because an AV Performance Code does not match any instance in Spektrix."
                )
                # ends program. nothing is saved
                sys.exit(1)

            seat_plan_id = instance_search.json()[0]["planId"]
            seat_type_search = tar.lookup_pricelist_of_instance(
                client_name, instance_id
            )
            # need to make sure you select the ticket type that costs 0 dollars
            selected_ticket_price_dict = {}
            for ticket_price_dict in seat_type_search.json()["prices"]:
                ticket_price = ticket_price_dict["amount"]
                if math.isclose(ticket_price, 0.0, abs_tol=1e-9):
                    selected_ticket_price_dict = ticket_price_dict
                    break
            seat_type_id = selected_ticket_price_dict["ticketType"]["id"]
            seat_type_name = selected_ticket_price_dict["ticketType"]["name"]

            event_id = instance_search.json()[0]["event"]["id"]
            event_lookup = tar.lookup_event_id(client_name, event_id)
            event_name = event_lookup.json()["name"]
            instance_dt = instance_search.json()[0]["start"]
            new_row = [
                shortened_avpc,
                instance_id,
                seat_plan_id,
                seat_type_id,
                seat_type_name,
                event_name,
                instance_dt,
            ]
            __insert_row_into_dataframe(instance_data_bank, new_row)
    print(
        """
=================================================================
Necessary ticketing data for each instance being imported has been extracted from the API.
Setting customer interest tags for each instance now.
================================================================="""
    )
    # now we tack on tag data
    # add three new columns Tag1 Tag2 Tag3
    instance_data_bank["Tag1"] = None
    instance_data_bank["Tag2"] = None
    instance_data_bank["Tag3"] = None
    __put_in_tag_data(instance_data_bank)

    # save to csv in subfolder
    subfolder = "past_output_files"
    filename = str(INCOMING_TIMESTAMP) + "_instance_databank.csv"
    file_path = os.path.join(subfolder, filename)
    instance_data_bank.to_csv(file_path, index=False, encoding="utf-8-sig")

    return instance_data_bank


# make list of incoming performance codes, match to instanceid seattype and seatplan
# output instance id bank to past imported data with timestamp to indicate which performances were imported before


if __name__ == "__main__":
    from pprint import pprint as pp

    pp("testing module.....")

    # read files into dataframes
    # in final ver dont ask for past imports csv, that remains invisible to user
    incoming_filename = input("Enter relative file path of incoming import csv:")
    incoming_import_df = pd.read_csv(incoming_filename)
    client_name = car.header_gen.k.client_name

    # set timestamp for incoming import
    INCOMING_TIMESTAMP = None
    manual_timestamp = input(
        "Would you like to manually input the timestamp of this import? If not, the current date and time will be used instead. y/n:"
    )
    if manual_timestamp == "y":
        INCOMING_TIMESTAMP = float(
            input(
                "Enter the date and time of the import data (cannot be exact same as another import) as a decimal number in the format YYYYMMDD.hhmm:"
            )
        )
    else:
        INCOMING_TIMESTAMP = float(datetime.now().strftime("%Y%m%d.%H%M"))

    instance_data_bank = databank_builder_and_printer(
        incoming_import_df, client_name, INCOMING_TIMESTAMP
    )
    pp(len(instance_data_bank))


# ================================================== sample code start ==================================================

# redacted

# basket = tar.agent_delivery_create_basket(customer_id_sns, client_sns)
# basket_id = basket.json()["id"]

# redacted

# ]
# body = []
# for avpc in avpcs:
#     instance_search = tar.search_instance_by_AVP_id(client_sns, avpc)
#     instance_id = instance_search.json()[0]["id"]
#     event = tar.lookup_event_id(client_sns, instance_search.json()[0]["event"]["id"])
#     pp(event.json()["name"])
#     pp(instance_search.json()[0]["id"])
#     seatplan_id = instance_search.json()[0]["planId"]
#     seat_type_search = tar.lookup_pricelist_of_instance(client_sns, instance_id)
#     seat_type = seat_type_search.json()["prices"][0]["ticketType"]["id"]
#     body = tar.BODY_BUILDER_RECURSIVE_add_tickets_to_basket(
#         instance_id, seat_type, seatplan_id, body
#     )

# res = tar.BASE_API_CALL_add_tickets_to_basket(basket_id, body, client_sns)
# pp("================ticket added, return below================")
# pp(res.ok)
# pp(res.json())

# end_basket = tar.lookup_basket(client_sns, basket_id)
# pp("================final basket check================")
# pp(end_basket.json())
# ================================================== sample code end ==================================================


# # ============================================================================
# # test insert row into dataframe

# columns = ["Shortened AVPC", "Instance ID", "Seat Type ID", "Seat Plan ID"]
# instance_data_bank = pd.DataFrame(columns=columns)
# new_row = ["blink", "blonk", "blank", "blunk"]
# __insert_row_into_dataframe(instance_data_bank, new_row)
# pp(instance_data_bank)
# __insert_row_into_dataframe(instance_data_bank, new_row)
# pp(instance_data_bank)

# # ============================================================================
