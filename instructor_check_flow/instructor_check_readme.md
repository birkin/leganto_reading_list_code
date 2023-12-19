# Summary...

(Processing the Spring 2024 reading-lists -- in December 2023.)

The "see file 'name-of-file'" entries refer to google-doc file-names.

- course-count from original OIT file (2023-Dec-19-Tuesday): 14,896
    - (see file "a__OIT_course_list...")
    - Note: had to manually make a slight manual correction to `brown.mcm.0800v.2024-spring` -- there was an errant backslash followed by an additional tab-character. Once they were removed, the file processed fine.



---------------------------------------------------------------------
old output start ----------------------------------------------------
---------------------------------------------------------------------

- course-count from original OIT file (2023-Nov-27-Monday): 14,885
    - (see file "a__OIT_course_list...")

- course-count from initial OIT subset: 1,389
    - filtered out courses not matching season-year (2024-spring), and not having section "s01", and not having an instructor.
    - (see output-file "b__oit_subset_01.tsv")
    - (see summary-file "b2__oit_data_01a_summary.json")

- course-count after filtering out courses with no email-address match: 1,260
    - I used OCRA to find email-addresses from the OIT Bru-ID.
    - (see output-file "c__oit_data_01b.json")

- course-count for remaining OIT courses after already-in-Leganto check: 1,056
    - 204 courses were removed because the course was already in Leganto with the same instructor.
    - (see file "d__already_in_leganto...tsv")
    - (see file "d2__oit_data_02.json")

- course-count for remaining OIT courses after OCRA class_id lookups: 311
    - 745 courses were removed because there were no OCRA class_ids found.
    - a "class_id" is required to do OCRA reading-list lookups.
    - I find class_ids by querying OCRA on the "department" and "number" part of the course-code (like "BIOL 1234")
    - (see file "e__oit_data_03.json")

- course-count for remaining OIT courses after matching (for each course) all OIT-instructors against all OCRA-instructors: 174
    - 137 courses were removed because there was no match between any of the OIT instructors and OCRA instructors.
    - (see file "f__oit_data_03b.json")

- course-count for remaining OIT courses after removing courses with no reading-list-data: 134
    - 40 courses were removed because there was no reading-list-data found.
    - (see file "g__oit_data_04.json")

- actual reading-list: see file "h__list_2023-11...tsv"

---------------------------------------------------------------------
old output end ------------------------------------------------------
---------------------------------------------------------------------


---------------------------------------------------------------------
standard ------------------------------------------------------------
---------------------------------------------------------------------


# Step 1 -- Initial OIT subset

script: "instructor_check_flow/10_prepare_oit_initial_subset.py"

source-file: see "a__OIT_course_list..." in the ""2024_spring_reading_list_stuff__Dec2023" folder.

output-files: 
- "csv_output/oit_subset_01.tsv"
- "json_data/oit_data_01b.json"

description:
This takes the full OIT course list, and produces a subset of courses for Spring 2024, eliminating:
- courses that are not offered in specified season-year (this specified season-year being spring-2024).
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

source-files: 
- "json_data/oit_data_01b.json"
- ../already_in_leganto_files/already_in_leganto_DATE_from_NAME.tsv

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

output-files: "csv_output/2023_summer/list_DATE-TIME.tsv"

description:
- This step creates a reading-list for each course in the source-json file.
- The OCRA data is enhanced by things like a CDL lookup, and reserves-uploader filename searches.

---

[END]
