import pandas as pd
from pprint import pprint as pp

instance_bank_filename = "past_output_files\\20241209.1416_instance_databank.csv"
instance_bank_df = pd.read_csv(instance_bank_filename)


term_to_search = "redacted"
print(
    term_to_search not in instance_bank_df["Shortened AVPC"].tolist()
)  # should evaluate to true
# have to use .tolist() otherwise the comparison doesnt work
print(term_to_search not in instance_bank_df["Shortened AVPC"].str.strip())
pp(instance_bank_df["Shortened AVPC"].str.strip())
