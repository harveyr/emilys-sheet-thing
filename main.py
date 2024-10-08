import logging

import pandas as pd
import streamlit as st


from typing import Optional

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


EM_COL_STUDENT_ID = "Student ID"
EM_COL_FIRST_NAME = "First Name"
EM_COL_LAST_NAME = "Last Name"
EM_COL_COURSE = "Course"
EM_COL_COURSE_NUM = "Course Number"


def main():
    st.title("Emily's thing")
    our_file = st.file_uploader("Our spreadsheet (Emily's)")
    their_file = st.file_uploader("Their spreadsheet")

    if our_file is not None:
        with st.spinner("Loading sheet..."):
            our_df = pd.read_excel(our_file)

        if their_file is not None:
            with st.spinner("Loading sheet..."):
                their_df = pd.read_excel(their_file)

            finish(ours=our_df, theirs=their_df)


def finish(ours: pd.DataFrame, theirs: pd.DataFrame):
    missing_theirs: pd.DataFrame = handle_ours_vs_theirs(ours=ours, theirs=theirs)
    missing_ours: pd.DataFrame = handle_theirs_vs_ours(ours=ours, theirs=theirs)

    for missing_key, df in [
        ("their", missing_theirs),
        ("our", missing_ours),
    ]:
        st.header(f"Registrations missing from {missing_key} sheet")
        st.download_button(
            "Download",
            df_to_csv(df),
            f"missing_from_{missing_key}s.csv",
            "text/csv",
            key=f"download-csv-missing-{missing_key}",
        )
        st.table(df)


def handle_ours_vs_theirs(ours: pd.DataFrame, theirs: pd.DataFrame) -> pd.DataFrame:
    missing = pd.DataFrame(columns=["ID", "Name", "Course"])

    for i, row in ours.iterrows():
        student_id: Optional[str] = row[EM_COL_STUDENT_ID]
        if not isinstance(student_id, str):
            student_id = None

        student_name = "{}, {}".format(
            row[EM_COL_LAST_NAME].strip(), row[EM_COL_FIRST_NAME].strip()
        )
        course_id = "{}{}".format(
            row[EM_COL_COURSE].strip(), str(row[EM_COL_COURSE_NUM]).strip()
        )

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
            msg = "No match: {} - {}".format(student_name, course_id)
            logger.info(msg)
            # st.write(msg)
            missing.loc[i] = [
                student_id or "[not found]",
                student_name,
                course_id,
            ]
        else:
            logger.debug("Match: {} - {}".format(student_name, course_id))

    return missing


def handle_theirs_vs_ours(ours: pd.DataFrame, theirs: pd.DataFrame) -> pd.DataFrame:
    missing = pd.DataFrame(columns=["ID", "Name", "Course Prefix", "Course Number"])

    for i, row in theirs.iterrows():
        student_id = row["ID"]
        student_name = row["Name"]
        course_id = row["COURSE"]

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
            # TODO: Find the rows in each sheet that have his name. Compare them.
            if "Ochiae" in student_name:
                from pprint import pprint

                pprint(
                    dict(
                        student_id=student_id,
                        student_name=student_name,
                        course_id=course_id,
                        course_prefix=course_prefix,
                        course_suffix=course_suffix,
                    )
                )

            if student_id != c_row[EM_COL_STUDENT_ID] and (
                first != c_row[EM_COL_FIRST_NAME] and last != c_row[EM_COL_LAST_NAME]
            ):
                # Neither student ID nor the names match
                continue

            if (
                course_id
                != c_row[EM_COL_COURSE].strip() + str(c_row[EM_COL_COURSE_NUM]).strip()
            ):
                # Course ID doesn't match
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
            ]

    return missing


def df_to_csv(df: pd.DataFrame):
    # Borrowed from https://docs.streamlit.io/knowledge-base/using-streamlit/how-download-pandas-dataframe-csv
    return df.to_csv(index=False).encode("utf-8")


if __name__ == "__main__":
    main()
