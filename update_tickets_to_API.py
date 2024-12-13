import pandas as pd
from cust_data_API_interactors import cust_API_requests as car
from cust_data_API_interactors import ticket_API_requests as tar
from cust_data_API_interactors import tag_related_API_requests as trar
import os
import string_cleaner


# uploads tickets to spektrix
# also checks that AVID/email combo lines up with account pulled from spektrix
# modifies incoming_import_df to flag errors or store successful order IDs
# outputs the modified df to csv in the folder past_output_files
def __generate_list_of_unique_emails(incoming_import: pd.DataFrame) -> list:
    unique_emails_list = incoming_import["Email"].unique().tolist()
    return unique_emails_list


# done tested
def __tag_customer_by_tickets_purchased(
    cust_id: str,
    avpc_databank: pd.DataFrame,
    filtered_by_email: pd.DataFrame,
    client_name: str,
) -> None:
    # build list of tags to attach to customer
    tags_to_add_to_cust = []
    # this is the list of instances attended
    avpc_list = filtered_by_email["Shortened Codes"].tolist()
    # look through avpc_list and avpc_databank to add the tags to tag_list
    for avpc in avpc_list:
        tags_for_this_instance = []
        ticker = 1
        while ticker <= 3:
            matching_series = avpc_databank.loc[
                avpc_databank["Shortened AVPC"] == avpc, "Tag" + str(ticker)
            ]
            if len(matching_series) == 1:
                tag_temp = matching_series.iloc[0]
            elif len(matching_series) == 0:
                tag_temp = None
            else:
                raise ValueError("Multiple matches found for the given condition")
            if tag_temp:
                tags_for_this_instance.append(tag_temp)
            ticker += 1
        for tag_temp_temp in tags_for_this_instance:
            if tag_temp_temp not in tags_to_add_to_cust:
                tags_to_add_to_cust.append(tag_temp_temp)

    # this func returns a dynamic class not a typical response
    add_tags_call = trar.add_tags_to_cust(tags_to_add_to_cust, cust_id, client_name)
    return add_tags_call


def update_tickets_to_API(
    incoming_import: pd.DataFrame,
    avpc_databank: pd.DataFrame,
    client_name: str,
    INCOMING_TIMESTAMP: float,
):
    # add row for flagging errors
    incoming_import["Error Flags"] = None
    # add row for transaction complete
    incoming_import["Successful Order ID"] = None

    # generate list of unique emails
    unique_emails_list = __generate_list_of_unique_emails(incoming_import)

    # for each unique email
    for email in unique_emails_list:

        # verify email is already connected to a customer in spektrix
        cust_search = car.lookup_cust_email(email, client_name)
        if not cust_search.ok:
            incoming_import.loc[incoming_import["Email"] == email, "Error Flags"] = (
                "CustEmailNoMatchSptxRec"
            )
            continue
        # get cust_id and av_id from call return
        cust_id = cust_search.json()["id"]
        av_id = cust_search.json()["attribute_AudienceViewID"]

        # verify that email/AVID combo in spektrix matches that in incoming import
        if str(av_id) != str(
            incoming_import.loc[
                incoming_import["Email"] == email, "Audienceview ID"
            ].iloc[0]
        ):
            incoming_import.loc[incoming_import["Email"] == email, "Error Flags"] = (
                "AVIDMatchError"
            )
            continue

        # create basket with customer and delivery attached. verify success
        basket_creation = tar.agent_delivery_create_basket(cust_id, client_name)
        if not basket_creation.ok:
            incoming_import.loc[incoming_import["Email"] == email, "Error Flags"] = (
                "BasketCreationError"
            )
            continue
        # save basket id
        basket_id = basket_creation.json()["id"]

        # now we can make tickets. filter the big df by the email
        filtered_by_email = incoming_import[
            incoming_import["Email"] == email
        ]  # returns a dataframe
        # build the ticket(s) body
        body = []
        for index, row in filtered_by_email.iterrows():
            # get the avpc
            row_dict = row.to_dict()
            avpc = string_cleaner.clean_text(row_dict["Shortened Codes"])
            # pull values that correspond to AV Perf Code from databank
            instance_id = avpc_databank.loc[
                avpc_databank["Shortened AVPC"] == avpc, "Instance ID"
            ].iloc[0]
            seat_type_id = avpc_databank.loc[
                avpc_databank["Shortened AVPC"] == avpc, "Seat Type ID"
            ].iloc[0]
            seatplan_id = avpc_databank.loc[
                avpc_databank["Shortened AVPC"] == avpc, "Seat Plan ID"
            ].iloc[0]
            body = tar.BODY_BUILDER_RECURSIVE_add_tickets_to_basket(
                instance_id, seat_type_id, seatplan_id, body
            )
        # add tickets to cart. verify success
        add_ticket_call = tar.BASE_API_CALL_add_tickets_to_basket(
            basket_id, body, client_name
        )
        if not add_ticket_call.ok:
            incoming_import.loc[incoming_import["Email"] == email, "Error Flags"] = (
                "TicketAddError"
            )
            continue

        # confirm basket. verify success
        checkout_call = tar.confirm_basket(basket_id, False, client_name)
        if not checkout_call.ok:
            incoming_import.loc[incoming_import["Email"] == email, "Error Flags"] = (
                "ConfirmBasketError"
            )
            continue

        # log successful order ID to the dataframe
        order_id = checkout_call.json()["id"]
        incoming_import.loc[
            incoming_import["Email"] == email, "Successful Order ID"
        ] = order_id

        # set tags for the customer
        __tag_customer_by_tickets_purchased(
            cust_id, avpc_databank, filtered_by_email, client_name
        )

    # output the modified df to csv in the folder past_output_files
    filename = str(INCOMING_TIMESTAMP) + "_post_completed_import.csv"
    subfolder = "past_output_files"
    filepath = os.path.join(subfolder, filename)
    incoming_import.to_csv(filepath, index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    from pprint import pprint as pp
    from datetime import datetime

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
