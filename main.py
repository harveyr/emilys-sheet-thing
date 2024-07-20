import logging

import pandas as pd
import streamlit as st

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def spike():
    logger.info("Loading Emily's sheet")
    emily = pd.read_excel(
        "/Users/harogers/Downloads/June RegistrationMaster.xlsx",
        usecols=[2, 3, 5, 6, 7],
        names=["last", "first", "prefix", "suffix", "title"],
    )

    logger.info("Loading their sheet")
    them = pd.read_excel("/Users/harogers/Downloads/June roster.xlsx")

    logger.info("Reading rows")
    for _, row in emily.iterrows():
        name = "{}, {}".format(row["last"].strip(), row["first"].strip())
        course = "{}{}".format(row["prefix"].strip(), str(row["suffix"]).strip())
        title = str(row["title"]).strip()

        filtered = them[
            (them["Name"].str.lower() == name.lower()) & (them["COURSE"] == course)
        ]

        if filtered.empty:
            logger.info("No match: {} - {} - {}".format(name, course, title))
        else:
            logger.debug("Match: {} - {} - {}".format(name, course, title))

    # dfs = {sheet_name: xl_file.parse(sheet_name)
    #         for sheet_name in xl_file.sheet_names}


def main():
    st.title("Emily's thing")


if __name__ == "__main__":
    # main()
    spike()
