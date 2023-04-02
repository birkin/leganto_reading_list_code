# Step 1 -- Initial OIT subset

script: "instructor_check_flow/10_prepare_oit_initial_subset.py"

source-file: N/A

output-file: "csv_output/oit_subset_01.tsv"

description:
This takes the full OIT course list, and produces a subset of courses for Summer 2023, eliminating:
- courses that are not offered in specified season-year (ie summer 2023).
- courses that either have no section, or have a section other than "s01".
- courses that have no instructor.

The output-file will be used as the source-file for the next 'create data-holder-dict' step.

---


# Step 1b -- create data-holder-dict

script: "instructor_check_flow/15_make_oit_subset_two.py"

source-file: "csv_output/oit_subset_01.tsv"

output-file: "json_data/oit_data_01b.json"

description:
- This takes the initial "oit_subset_01.tsv" file, and creates a data-holder-dict of relevant data. 
- It also takes the OIT bru_id(s), and looks for the relevant instructor email-address(es) in OCRA, creating, for each data-holder-dict item, a bru_id-to-email-address map field, and an email-addresses field.
- OIT entries that have no email-address match are eliminated.
- The output-file will be used as the source-file for the next 'Leganto lookup' step.

---


# Step 2 -- Leganto lookup

script: "instructor_check_flow/20_make_oit_subset_two.py"

source-file: "json_data/oit_data_01b.json"

output-file: "json_data/oit_data_02.json"

description:
- This takes the data-holder-dict from "oit_data_01b.json", and looks for a matching entry in Leganto.
- The new subset file will remove courses from the original subset file if the course is already in Leganto with the same instructor.
    - Otherwise, the OIT course will be kept for the next step of doing OCRA reading-list-data lookups.
- The output-file will be used as the source-file for the next 'OCRA lookups' step.

---


# Step 3 -- OCRA class_id lookups

script: "instructor_check_flow/30_get_ocra_classids.py"

source-file: "json_data/oit_data_02.json"

output-file: "json_data/oit_data_03.json"

description:
- This step queries ocra for each remaining OIT course to get "class_ids".
- Courses with no class_ids are removed.
- The class_ids will be used in the next step to get reading-list-data.


---


# Step 3b -- get OCRA emails

script: "instructor_check_flow/35_get_ocra_emails.py"

source-file: "json_data/oit_data_03.json"

output-file: "json_data/oit_data_03b.json"

description:
- For each remaining OIT course, this script queries OCRA on all the course's "class_ids" to get the OCRA email-address for the class_id.
- courses where there is no match between any of the OIT instructors and OCRA instructors are removed.
    - You can see the courses removed in the __meta__ section "oit_courses_removed_list".
    - A course is removed if there is no match between the "oit_email_addresses" and the "ocra_class_id_to_instructor_email_map" fields.
- Reading-list lookups will be done on the class-ids in the "ocra_class_id_to_instructor_email_map_for_matches" field.

---


# Step 4 -- gather reading-list-data

script: "instructor_check_flow/40_get_reading_list_data.py"

source-file: "json_data/oit_data_03b.json"

output-file: "json_data/oit_data_04.json"

description:
- For each remaining course: this step queries ocra on each class_id to get reading-list-data.
- It queries OCRA on article, audio, book, ebook, excerpt, tracks, video, and website results.
- Courses that have no reading-list-data are removed.

---


# Step 5 -- Create reading-list files

script: "instructor_check_flow/50_create_reading_lists.py"

source-file: "json_data/oit_data_04.json"

output-files: "csv_output/get-reading-list-pattern.tsv"

description:
- This step will create a reading-list for each course in the data-holder-dict.

---
