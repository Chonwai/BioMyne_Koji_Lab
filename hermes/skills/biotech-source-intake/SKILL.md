# biotech-source-intake

## Purpose

Load the biotech source manifest and prepare crawl tasks for the current run.

## Inputs

- `manifest_path`: path to the YAML source manifest

## Outputs

- `sources`: validated enabled sources
- `task_count`: integer
- `validation_errors`: list

## Procedure

1. Read the YAML manifest.
2. Filter `enabled: true` sources.
3. Validate required fields (`name`, `url`, `source_type`, `crawl_frequency`).
4. Return a structured result for downstream crawl execution.

## Failure Rules

- invalid manifest structure => fail fast
- invalid single source row => collect error and continue validation
