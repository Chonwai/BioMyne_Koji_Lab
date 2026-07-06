# biotech-digest-publish

## Purpose

Aggregate the highest-value outputs from a run and render a concise digest for the selected delivery channel.

## Inputs

- `crawl_run_id`
- `articles`
- `delivery_channel`

## Outputs

- `digest_text`
- `top_items_count`
- `delivery_result`

## Procedure

1. Rank articles by priority and relevance.
2. Select the top 3-5 items.
3. Render the digest in the approved channel format.
4. Record delivery outcome.

## Failure Rules

- if delivery fails, record the failure and notify operator
- do not silently drop digest output
