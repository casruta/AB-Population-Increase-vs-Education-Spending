# School matching and migration-related service needs

The official class-size, school composition and school occurrence workbooks use
the same 24 November 2025 ACIP collection, with public, separate and francophone
coverage and the same exclusions described in FINDINGS.md. Their keys support
local evaluation planning, rather than a causal migration effect.

|Workbook|Authority key|School key|Data grain|
|---|---|---|---|
|class-size-2025-2026.xlsx|column C `Auth Code`|column D `School Code`|Teacher/group instructional class record|
|composition-by-school-2025-2026.xlsx|column B `Authority Code`|column D `School Code`|School totals of reportable classes by category-count band|
|occurrence-by-school-2025-2026.xlsx|column B `Authority Code`|column D `School Code`|School totals of reportable classes by occurrence band|

Preserve zero-padding and treat keys as strings. Join on authority plus school
codes, not school names. Aggregate classroom rows to school before joining school
summaries; do not multiply school totals across repeated classroom records.
Check unmatched keys, excluded programs and suppression before interpreting
authority totals. School codes match a service-delivery unit, not longitudinal
student identities. No student-level identifier exists to deduplicate pupils.

Composition counts how many of nine categories occur in each class. Categories
include EAL, mild/moderate needs, severe needs, IPP, First Nations/Métis/Inuit,
gifted, refugee, assessment waitlist and other. Categories can overlap, and school
authorities can use local assessments or observations as well as provincial
coding criteria. Indigenous identity, giftedness or multilingualism must not be
interpreted as deficits or interchangeable support requirements.

Occurrence combines EAL, mild/moderate and severe needs. High means at least 11
students with these combined needs in a classroom, medium 5–10, low 0–4. The
school workbook reports classroom counts in those bands. It does not report
EAL-only pupil counts. Students repeat across classroom records, and categories
overlap. There is no verified unique EAL numerator or unique pupil denominator,
so no EAL prevalence or migration-driven demand estimate is justified.

EAL is not equivalent to newly arrived international migration. Some EAL students
were born in Canada; recent arrivals can have different languages, prior schooling,
ages, circumstances and support needs. Class size or composition does not show
that a school lacks staff or that the same pupils caused an outcome change.

For a targeted Grades 7–9 mathematics support pilot, authorities can combine
these school snapshots with locally governed diagnostic assessments, attendance,
language-support requirements, recent arrival where relevant, vacancies,
actual teaching/support hours and service waits. Treat overlapping needs separately
and protect student data. Match spending and headcounts to the same authority
scope and periods; observe implementation before evaluating achievement changes.
Compare phased support schools with credible comparison schools and pre-existing
trends, with cohort and participation checks. Provincial migration totals cannot
substitute for school-specific enrolment or need.

# Expanded freshness checks

The complete live catalogue searches saved here include:

- `all-education-annual-search.json`: seven records for annual-report titles with
  education or childcare; latest Education annual report resource remains 2024–25.
- `annual-childcare-fulltext-search.json`: two records for annual-report title
  plus childcare anywhere; Education update and Teaching Profession Commission.
- `annual2025-2026-fulltext-search.json`: fourteen complete records for literal
  2025-2026, education and annual; no later ministry annual report.
- `annual2025-26-fulltext-search.json`: thirteen complete records for alternate
  year spelling; no later ministry annual report. This search discovered the
  companion composition and occurrence datasets.
- `all-assurance-search.json`: 57 complete assurance-title records; latest
  education outcome report is Fall 2025. 2026 education assurance documents are
  methodology publications, not fresh outcome results.
- `goa-annual-search.json`: 61 complete Alberta annual-report records; Government
  of Alberta annual report latest resource is 2024–25, despite April 2026 metadata
  modification. No Government of Alberta 2025–26 outcome release was located.
- Live official annual-reports and accountability-education-system pages link
  the same 2024–25 annual/update and Fall 2025 assurance results/authority summaries.

These checks cover the renamed Education and Childcare ministry as well as
Education. They justify 'latest verified/located', not proof that a later release
does not exist. The 2026–29 business plan explicitly expected 2024–25 completion
data in June 2026; that expected release remains a freshness gap in this review.

Two complete publisher-filtered searches explicitly cover the ministry rename:
`childcare-organization-annual-search.json` (two annual-title records from
Education and Childcare) and `education-organization-annual-title-search.json`
(25 annual-title records from Education). Both give the same latest located
2024–25 outcome source. A broader Education publisher query was truncated and
is not used to justify completeness.

School-key validation found 88,932 distinct classroom identifiers and 1,560
class-workbook authority/school keys. Both companions contain 1,549 unique school
keys, all matched to the class workbook. Eleven class-workbook schools lack a
companion record; check these omissions before integrating school-level results.
`school-key-validation.json` saves the counts.
