# Step 1 -- Initial OIT subset

This takes the full OIT course list, and produces a subset of courses for Summer 2023, eliminating:
- courses that are not offered in specified season-year (ie summer 2023).
- courses that either have no section, or have a section other than "s01".
- courses that have no instructor.

The output is "/csv_output/oit_subset_01.tsv"

---


# Step 2 -- Second OIT subset

Eliminate courses that already have an entry in Leganto (based on course-code + course-number).

The output will be "/csv_output/oit_subset_02.tsv"

---


# Step 3 -- Third OIT subset
