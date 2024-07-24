import logging

import pandas as pd
import streamlit as st


from typing import Optional

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    st.title("Emily's thing")
    emily_file = st.file_uploader("Our spreadsheet (Emily's)")
    theirs_file = st.file_uploader("Their spreadsheet")

    if emily_file is not None:
        with st.spinner("Loading sheet..."):
            ours_df = pd.read_excel(
                emily_file,
                usecols=[0, 2, 3, 5, 6, 7],
                names=["student_id", "last", "first", "prefix", "suffix", "title"],
            )

        if theirs_file is not None:
            with st.spinner("Loading sheet..."):
                theirs_df = pd.read_excel(theirs_file)

            handle_ours_vs_theirs(ours=ours_df, theirs=theirs_df)
            handle_theirs_vs_ours(ours=ours_df, theirs=theirs_df)


def handle_theirs_vs_ours(ours: pd.DataFrame, theirs: pd.DataFrame):
    missing = pd.DataFrame(
        columns=["ID", "Name", "Course Prefix", "Course Number", "Title"]
    )

    for i, row in theirs.iterrows():
        student_id = row["ID"]
        student_name = row["Name"]
        course_id = row["COURSE"]
        course_title = row["TITLE"]

        if not isinstance(student_id, str):
            if not isinstance(course_id, str):
                # This is an empty row
                continue

            raise ValueError(
                f"Found a non-string student ID in theirs: {student_id} "
                f"({student_name})"
            )

        first, last = [s.strip() for s in student_name.split(",")]
        course_id: str = course_id.strip()
        course_prefix = course_id[:4]
        course_suffix = course_id[4:]

        matched = False

        for _, c_row in ours.iterrows():
            if student_id != c_row["student_id"] and (
                first != c_row["first"] and last != c_row["last"]
            ):
                continue

            if course_id != c_row["prefix"].strip() + str(c_row["suffix"]).strip():
                continue

            matched = True
            logger.info("Match: %s, %s", student_name, course_id)
            break

        if not matched:
            missing.loc[i] = [
                student_id,
                student_name,
                course_prefix,
                course_suffix,
                course_title,
            ]

    st.header("Registrations in their sheet missing from ours")
    st.table(missing)


def handle_ours_vs_theirs(ours: pd.DataFrame, theirs: pd.DataFrame):
    missing = pd.DataFrame(columns=["ID", "Name", "Course", "Title"])

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
            missing.loc[i] = [
                student_id or "[not found]",
                student_name,
                course_id,
                course_title,
            ]
        else:
            logger.debug(
                "Match: {} - {} - {}".format(student_name, course_id, course_title)
            )

    st.header("Registrations in our sheet missing from theirs")
    st.table(missing)


if __name__ == "__main__":
    main()
    # spike()
