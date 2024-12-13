from datetime import datetime
import pandas as pd
from cust_data_API_interactors import keys as k
from build_avpc_databank import databank_builder_and_printer
from update_tickets_to_API import update_tickets_to_API
import sys

# read files into dataframes
# in final ver dont ask for past imports csv, that remains invisible to user
incoming_filename = input("Enter relative file path of incoming import csv:")
incoming_import = pd.read_csv(incoming_filename)
client_name = k.client_name

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

# builds databank of instance data
# outputs timestamped databank of instance data necessary for ticketing into csv in the folder past_output_files
databank_of_AV_performance_codes = databank_builder_and_printer(
    incoming_import, client_name, INCOMING_TIMESTAMP
)

print("The databank that matches AV Performance Codes to the correct ticketing and tagging data has been generated.")
proceed_with_ticket_import = input("Proceed with import? y/n: ")
if proceed_with_ticket_import != "y":
    sys.exit()
print("Importing tickets...this will take a little while, about 3 seconds per ticket being processed.")
# uploads tickets to spektrix
# modifies incoming import df to flag errors and record successful order IDs, and outputs that to csv in the folder past_output_files
# consider adding customer tags for future feature improvement
update_tickets_to_API(
    incoming_import, databank_of_AV_performance_codes, client_name, INCOMING_TIMESTAMP
)

print("All done!")
