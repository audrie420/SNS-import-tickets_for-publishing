import re
import pandas as pd

def clean_text(text):
    return re.sub(r'[\u2000-\u206F]', '', text)

def clean_dataframe(df: pd.DataFrame):
    return df.apply(lambda row: [clean_text(cell) if isinstance(cell, str) else cell for cell in row], axis=1)

if __name__ == "__main__":
    from pprint import pprint as pp
    mystr = "\u2060Ok Google how do i turn on my monitor"
    print(mystr)
    pp(mystr)
    pp(repr(mystr))
    pp(clean_text(mystr))