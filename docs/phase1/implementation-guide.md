# Phase 1 Implementation Guide

## Goal

Turn the approved Phase 1 specification into a working repo baseline and a manually executable intelligence loop.

## Day 1

- create / verify Supabase project
- apply SQL migrations
- fill `.env.example`
- install Hermes Agent and Ollama
- create and verify one Ollama model tag

## Day 2

- finalize `biotech.yaml`
- complete three SKILL.md scaffolds
- validate source manifest
- run one source-level fetch test

## Day 3

- validate one article analysis prompt/output cycle
- verify Supabase persistence path
- verify Langfuse trace path
- prepare one sample digest

## Smoke Test Gate

Do not enable recurring scheduled runs until:

- one article can be fetched
- one JSON output is schema-valid
- one article row persists to Supabase
- one digest can be rendered and delivered
- one Langfuse trace can be observed
