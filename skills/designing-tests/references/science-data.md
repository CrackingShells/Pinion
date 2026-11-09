# The study contract: data that can be swapped and compared

## Contents

- The manifest
- The data dictionary
- Provenance
- The evolution log
- Checking and comparing
- What check does not catch

A battery of statistical tests lives as long as the research question it answers, and the
datasets under it keep changing: a rerun, a new cohort, a simulation under the null, a
simulation under the effect that matters. If every agent saves data its own way, nobody can say
whether a new dataset may be fed to the existing battery, or whether two studies are comparable.
The study contract makes the shape of the data checkable, so that question has an answer before
the battery runs. It serves three needs: swapping a dataset under a battery, comparing two
studies, and starting a manifest from a data file's header. It chooses no test and runs no
analysis; choosing and validating tests is in
[science-questions-and-tests.md](science-questions-and-tests.md).

## The manifest

One JSON file per study, shaped by [assets/study-contract.schema.json](../assets/study-contract.schema.json).
Paths inside it are relative to the manifest's own directory, so the folder can move.

- `contract_version`: must equal the last segment of the schema's `$id`. A breaking change to the
  schema ships as a breaking release of the skill, so a manifest written for another version is
  rejected instead of half-read.
- `study`, `research_questions`, `statistical_questions`: the ids that tie data to the questions
  the battery answers. Without them a dataset is orphaned from the reason it exists.
- `protocol_version`: the protocol the data were produced under. Two studies run under different
  protocols are not comparable even when their columns agree; `compare` reports the difference.
- `datasets`: each has a unique `id` (`compare` pairs datasets of two studies by it, so keep the
  id stable when you swap the data), a `path`, a `format` (`csv` or `tsv`), an `origin`
  (`simulated-null`, `simulated-effect`, `pilot`, `real`, which tells a reader how far to trust a
  result), a dictionary, provenance and a `unit`.
- `unit`: the name of the dictionary variable whose levels are independent observations: the
  subject, the plate, the site. It may repeat across rows. It is not the row key: the variables
  with role `id` key the rows jointly, and that combination must not repeat. For repeated
  measures, id = subject + time and unit = subject. The unit is what a battery treats as one
  observation, so a study with one row per subject and a study with several rows per subject are
  different shapes even when the columns match, and `compare` says so.

## The data dictionary

An example that validates: [assets/data-dictionary.example.json](../assets/data-dictionary.example.json).
Put it inline in the manifest, or in its own file and give its path, when several datasets share
it. Per variable:

- `name` exactly as in the header, and `type` (`integer`, `number`, `string`).
- `units`, required for numeric variables: a column of numbers whose unit is unknown is the usual
  reason two datasets that "match" do not. Write `unitless` when there are none, so absence is a
  decision and not an omission.
- `allowed_values` or `range` (inclusive, numeric variables only, min not above max): the values
  the battery can rely on. A factor must list its `allowed_values`; the problem message shows the
  levels found in the file to copy from. A sentinel such as -999 is caught only by a range, so
  declare one.
- `missing_codes`: the cells that mean "no value" for this variable. The script knows common
  missing-looking cells (empty, whitespace, `NA`, `NaN`, `null`, `.`) and reports each one the
  variable does not declare, rather than guessing whether it is data.
- `role`: `id`, `factor`, `outcome` or `covariate`. A dataset needs at least one `id` and one
  `outcome` variable, and an outcome that is missing in every row is a problem.
- `description`: for the next reader, who has only this file.

## Provenance

`instrument` (a device, a survey, a simulator and its version) and `dates` are required; add
`code_commit` whenever code produced or processed the data. `seeds` is required, and non-empty,
when the origin is `simulated-null` or `simulated-effect`: a simulation without its seed cannot
be regenerated as the known-truth run it was meant to be
([science-protocol-and-sample.md](science-protocol-and-sample.md)). Provenance is what lets a
dataset be regenerated or distrusted later.

## The evolution log

`evolution_log` records every change to the plan or protocol after it was first fixed. It is a
record, not a verdict: a change is neither good nor bad, only something a reader must be able to
find. Each entry has six fields, all required, the ones the analysis plan asks for
([science-analysis-plan.md](science-analysis-plan.md)): `date`; `stage` (before any data, after a
pilot or a simulation, after the data of this study were seen); `change` (old and new content);
`reason`; `agreed_by`; `effect_on_claim` (which results stay confirmatory, which become
exploratory). The log starts empty. The script requires the fields but does not compare logs
between studies.

## Checking and comparing

Run from the project, with `<skill-dir>` standing for this skill's base directory. These commands
are fixed; everything around them is yours.

```
uv run <skill-dir>/scripts/study_contract.py init <data.csv|data.tsv ...> [--out study-manifest.json]
uv run <skill-dir>/scripts/study_contract.py check <manifest.json>
uv run <skill-dir>/scripts/study_contract.py compare <a.json> <b.json>
```

`init` writes a manifest from the headers, with `TODO` wherever you must decide, and refuses to
overwrite a file. It cannot know your units, ranges, roles or unit of independence: fill them in
from what you know of the data, and ask when you do not.

Validate, fix, repeat: run `check`, fix what it lists, run it again until the first line is
`RESULT=OK`. Nothing is a warning: everything it lists is a problem, so `OK` means one thing. Do not run the
battery on a dataset before it. Reading the result:

| First line | Exit | Meaning |
|---|---|---|
| `RESULT=OK` | 0 | the manifest and every dataset conform |
| `RESULT=PROBLEMS n` | 1 | n problems, one per line, each naming what was expected and what is available |
| `RESULT=SWAPPABLE` | 0 | `compare`: same dictionaries, units, protocol and contract version |
| `RESULT=DIFFERS n` | 1 | `compare`: n differences, each naming the variable and both values |
| (an error message) | 64 | a bad argument: unknown flag, unreadable file, or, for `compare`, a manifest that breaks the schema |

`check` reports in layers: a manifest that breaks the schema, is still incomplete, or declares
another contract version stops there, and the data checks follow once it is sound. Counts are of
problems, with a few example lines each, not of bad cells.

`compare` compares contracts, never data: it does not open a data file. Run `check` on both
manifests first and get `RESULT=OK`, or a `SWAPPABLE` means only that two descriptions agree, not
that the files do. It ignores what does not change the shape (paths, origin, provenance, study id,
descriptions, the evolution log, the order of variables and of allowed values) and reports
everything else, the unit included. When it says `DIFFERS`, decide whether the battery still
applies; the script does not.

## What check does not catch

The script is the floor. These are left to you, the battery and the plan:

- A factor with a single level, or groups of very different sizes: whether either breaks a test
  depends on the battery.
- A declared unit that is wrong: units are trusted.
- Swapped group labels, or any mistake that leaves the values legal.
- Clusters, pairing, time and event status: the contract names one unit and the id keys, nothing
  more. The protocol section of the analysis plan carries the rest.

Look at the data as well.
