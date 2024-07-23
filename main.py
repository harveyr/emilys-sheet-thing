import logging

import pandas as pd
import streamlit as st
import math

from typing import Optional

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    st.title("Emily's thing")
    emily_file = st.file_uploader("Emily's spreadsheet")
    theirs_file = st.file_uploader("Their spreadsheet")

    if emily_file is not None:
        ours_df = pd.read_excel(
            emily_file,
            usecols=[0, 2, 3, 5, 6, 7],
            names=["student_id", "last", "first", "prefix", "suffix", "title"],
        )

        if theirs_file is not None:
            theirs_df = pd.read_excel(theirs_file)

            handle(ours=ours_df, theirs=theirs_df)


def handle(ours: pd.DataFrame, theirs: pd.DataFrame):
    missing_theirs = pd.DataFrame(columns=["ID", "Name", "Course", "Title"])

    for i, row in ours.iterrows():
        student_id: Optional[str] = row["student_id"]
        if not isinstance(student_id, str):
            student_id = None

        student_name = "{}, {}".format(row["last"].strip(), row["first"].strip())
        course_id = "{}{}".format(row["prefix"].strip(), str(row["suffix"]).strip())
        course_title = str(row["title"]).strip()

        filtered: pd.Series = None
        if student_id:
            filtered = theirs[
                (theirs["ID"] == student_id) & (theirs["COURSE"] == course_id)
            ]
        else:
            # No ID. Compare by name
            filtered = theirs[
                (theirs["Name"].str.lower() == student_name.lower())
                & (theirs["COURSE"] == course_id)
            ]

        if filtered.empty:
            msg = "No match: {} - {} - {}".format(student_name, course_id, course_title)
            logger.info(msg)
            # st.write(msg)
            missing_theirs.loc[i] = [
                student_id or "[not found]",
                student_name,
                course_id,
                course_title,
            ]
        else:
            logger.debug(
                "Match: {} - {} - {}".format(student_name, course_id, course_title)
            )

    st.header("Registrations missing from their sheet")
    st.table(missing_theirs)


if __name__ == "__main__":
    main()
    # spike()
