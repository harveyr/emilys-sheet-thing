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
    emily_file = st.file_uploader("Emily's spreadsheet")
    them_file = st.file_uploader("Their spreadsheet")

    if emily_file is not None:
        emily_df = pd.read_excel(
            emily_file,
            usecols=[2, 3, 5, 6, 7],
            names=["last", "first", "prefix", "suffix", "title"],
        )

        if them_file is not None:
            them_df = pd.read_excel(them_file)

            handle(emily=emily_df, them=them_df)


def handle(emily: pd.DataFrame, them: pd.DataFrame):
    for _, row in emily.iterrows():
        name = "{}, {}".format(row["last"].strip(), row["first"].strip())
        course = "{}{}".format(row["prefix"].strip(), str(row["suffix"]).strip())
        title = str(row["title"]).strip()

        filtered = them[
            (them["Name"].str.lower() == name.lower()) & (them["COURSE"] == course)
        ]

        if filtered.empty:
            msg = "No match: {} - {} - {}".format(name, course, title)
            logger.info(msg)
            st.write(msg)
        else:
            logger.debug("Match: {} - {} - {}".format(name, course, title))


if __name__ == "__main__":
    main()
    # spike()
