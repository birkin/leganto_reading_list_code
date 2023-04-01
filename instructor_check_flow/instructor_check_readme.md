# Step 1 -- Initial OIT subset

script: "instructor_check_flow/10_prepare_oit_initial_subset.py"

output: "csv_output/oit_subset_01.tsv"

description:
This takes the full OIT course list, and produces a subset of courses for Summer 2023, eliminating:
- courses that are not offered in specified season-year (ie summer 2023).
- courses that either have no section, or have a section other than "s01".
- courses that have no instructor.

---

# Step 1b -- create data-holder-dict

script: ""

output: ""

description:
""

---

# Step 2 -- Second OIT subset

Eliminate courses that already have an entry in Leganto (based on course-code + course-number).

The output will be "/csv_output/oit_subset_02.tsv"

---


# Step 3 -- Third OIT subset
