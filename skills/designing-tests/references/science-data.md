# The study contract: data that can be swapped and compared

A battery of statistical tests lives as long as the research question it answers, and the
datasets under it keep changing: a rerun, a new cohort, a simulation under the null, a
simulation under the effect that matters. If every agent saves data its own way, nobody can say
whether a new dataset may be fed to the existing battery, or whether two studies are comparable.
The study contract makes the shape of the data checkable, so that question has an answer before
the battery runs. It serves exactly three needs: swapping a dataset under a battery, comparing
two studies, and starting a manifest from a data file's header. It chooses no test and runs no
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
  result), a dictionary and provenance.

## The data dictionary

An example that validates: [assets/data-dictionary.example.json](../assets/data-dictionary.example.json).
Put it inline in the manifest, or in its own file and give its path, when several datasets share
it. Per variable:

- `name` exactly as in the header, and `type` (`integer`, `number`, `string`).
- `units`, required for numeric variables: a column of numbers whose unit is unknown is the usual
  reason two datasets that "match" do not. Write `unitless` when there are none, so absence is a
  decision and not an omission.
- `allowed_values` or `range` (inclusive): the values the battery can rely on. A sentinel such as
  -999 is caught only by a range, so declare one.
- `missing_codes`: the cells that mean "no value" for this variable. The script knows common
  missing-looking cells (empty, `NA`, `NaN`, `null`, `.`) and reports each one the variable does
  not declare, rather than guessing whether it is data.
- `role`: `id`, `factor`, `outcome` or `covariate`. Rows are identified by the `id` columns, which
  must not repeat. The battery reads roles, so a changed role is a changed study.
- `description`: for the next reader, who has only this file.

## Provenance

`instrument` (a device, a survey, a simulator and its version) and `dates` are required; add
`code_commit` and `seeds` whenever code produced or processed the data. Provenance is what lets a
dataset be regenerated or distrusted later; a simulated-null dataset without its seed cannot be
reproduced as the known-truth run it was meant to be
([science-protocol-and-sample.md](science-protocol-and-sample.md)).

## The evolution log

`evolution_log` records every change to the plan or protocol after it was first fixed: date,
what changed, why. It is a record, not a verdict: a change is neither good nor bad, only
something a reader must be able to find. It starts empty, and the script does not compare it
between studies.

## Checking and comparing

Run from the skill directory. These commands are fixed; everything around them is yours.

```
uv run scripts/study_contract.py init <data.csv|data.tsv ...> [--out study-manifest.json]
uv run scripts/study_contract.py check <manifest.json>
uv run scripts/study_contract.py compare <a.json> <b.json>
```

`init` writes a manifest from the headers, with `TODO` wherever you must decide, and refuses to
overwrite a file. It cannot know your units, ranges or roles: fill them in from what you know of
the data, and ask when you do not.

Validate, fix, repeat: run `check`, fix what it lists, run it again until the first line is
`RESULT=OK`. Do not run the battery on a dataset before that. Reading the result:

| First line | Exit | Meaning |
|---|---|---|
| `RESULT=OK` | 0 | the manifest and every dataset conform |
| `RESULT=PROBLEMS n` | 1 | n problems, one per line, each naming what was expected and what is available |
| `RESULT=SWAPPABLE` | 0 | `compare`: same dictionaries, same protocol and contract version |
| `RESULT=DIFFERS n` | 1 | `compare`: n differences, each naming the variable and both values |
| (an error message) | 64 | a bad argument: unknown flag, unreadable file, or, for `compare`, a manifest that does not pass `check` |

`check` reports in layers: a manifest that breaks the schema, is still incomplete, or declares
another contract version stops there, and the data checks follow once it is sound. Counts are of
problems, with a few example lines each, not of bad cells. `compare` ignores what does not change
the shape: paths, origin, provenance, study id, descriptions, the evolution log and the order of
variables. When it says `DIFFERS`, decide whether the battery still applies; the script does not.

The script is the floor, not the ceiling. A dataset that passes may still be wrong in ways a
dictionary cannot say (a swapped label, a unit that is declared and mistaken); look at the data.
