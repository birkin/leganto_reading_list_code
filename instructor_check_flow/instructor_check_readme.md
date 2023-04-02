# Step 1 -- Initial OIT subset

script: "instructor_check_flow/10_prepare_oit_initial_subset.py"

source-file: N/A

output-file: "csv_output/oit_subset_01.tsv"

description:
This takes the full OIT course list, and produces a subset of courses for Summer 2023, eliminating:
- courses that are not offered in specified season-year (ie summer 2023).
- courses that either have no section, or have a section other than "s01".
- courses that have no instructor.

---

# Step 1b -- create data-holder-dict

script: "instructor_check_flow/15_make_oit_subset_two.py"

source-file: "csv_output/oit_subset_01.tsv"

output-file: "json_data/oit_data_01b.json"

description:
- This takes the initial "oit_subset_01.tsv" file, and creates a data-holder-dict of relevant data. 
- It also takes the OIT bru_id(s), and looks for the relevant instructor email-address(es) in OCRA, creating, for each data-holder-dict item, a bru_id-to-email-address map field, and an email-addresses field.
- OIT entries that have no email-address match are eliminated.

---

# Step 2 -- Leganto lookup

script: "instructor_check_flow/20_make_oit_subset_two.py"

source-file: "json_data/oit_data_01b.json"

output-file: "json_data/oit_data_02.json"

description:
- This takes the data-holder-dict from "oit_data_01b.json", and looks for a matching entry in Leganto.
- The new subset file will remove courses from the original subset file if the course is already in Leganto with the same instructor.
    - Otherwise, the OIT course will be kept for the next step of doing OCRA reading-list-data lookups.

---

# Step 3 -- OCRA lookups

script: "instructor_check_flow/30_extract_data_from_ocra.py"

HEREZZ

source-file: "json_data/oit_data_02.json"

output-file: "json_data/oit_data_03.json"

description:
- This step will query OCRA for each course in the data-holder-dict, and add the OCRA data to the data-holder-dict.
- It will then remove any reading-list entries where the instructor is not one of the OIT-course instructors.
- It will then remove any course without any reading-list data.

---


# Step 4 -- Create reading-lists

script: "instructor_check_flow/40_create_reading_lists.py"

source-file: "json_data/oit_data_03.json"

output-files: "csv_output/get-reading-list-pattern.tsv"

description:
- This step will create a reading-list for each course in the data-holder-dict.

---
