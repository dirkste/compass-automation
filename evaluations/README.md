# Evaluations Directory

This directory contains completed code evaluation checklists for branch integration assessments.

## Purpose

Each evaluation document provides:
- Complete evidence-based analysis of branch readiness
- Test validation results and documentation review
- Risk assessment and integration recommendations
- Historical record of evaluation decisions

## Usage

1. Generate new evaluation: `python generate_evaluation.py <branch-name>`
2. Complete all checklist sections with concrete evidence
3. Make integration decisions based only on completed evaluations
4. Archive completed evaluations for historical reference

## File Naming Convention

`evaluation_<branch-name>_<timestamp>.md`

Example: `evaluation_feature_next-development_20251109_143022.md`

## Standards Reference

All evaluations must follow the criteria in:
- `../CODE_EVALUATION_STANDARDS.md` - Complete evaluation standards
- `../EVALUATION_CHECKLIST_TEMPLATE.md` - Template for new evaluations

## Important Notes

- **Never make integration recommendations without completed evaluation**
- **All test results must be evidence-based with actual execution logs**
- **E2E tests must complete full workflows, not just setup phases**
- **Document all assumptions and validate them**