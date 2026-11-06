# CAD Fun — Scoring System (Version 1 draft)

## 1. Purpose

This document defines how the backend compares submitted CAD parameters with the expected parameters and converts those differences into scores.

The frontend displays the results. It must not independently calculate authoritative assessment scores.

## 2. Core principles

- Each question has expected parameter values.
- Each assessed parameter has a comparison rule, tolerance, and weight.
- An error describes the difference between submitted and expected values.
- A score describes the points awarded for that criterion, from 0 to 100.
- The overall score is a weighted average of the enabled criteria.
- Tolerances and weights must be configured deliberately; agents must not invent them.

## 3. Error definitions

For a numeric scalar such as volume, the recommended reported error is absolute percentage error:

`error_percent = abs(submitted - expected) / abs(expected) * 100`

Special case: if the expected value is zero, percentage error is undefined. Use absolute error for that comparison, with a question-specific absolute tolerance.

For vector parameters such as center of mass and bounding-box dimensions, report component-wise absolute differences:

`error = [abs(dx), abs(dy), abs(dz)]`

For integer counts, report absolute count difference:

`error = abs(submitted_count - expected_count)`

For face-type counts, report the absolute difference for each surface type. Types missing from either map are treated as having count zero. The backend should return the union of types present in the expected and submitted maps so missing types are visible.

The exact error unit must be included in implementation and, where appropriate, response metadata or field descriptions. Do not label an absolute difference as a percentage.

## 4. Score calculation

A recommended simple tolerance-based scoring function is:

`parameter_score = max(0, 100 * (1 - normalized_error / tolerance))`

Where:
- `normalized_error` is the parameter's defined error measure;
- `tolerance` is the accepted maximum error for that criterion;
- a zero or negative tolerance is invalid;
- a score is clamped to the range 0–100.

For vector parameters, the question configuration must specify whether normalized error is the maximum component error or another explicit aggregate. The recommended initial choice is maximum component error.

For face-type maps, use the maximum absolute count difference across all surface types unless a different aggregation is explicitly configured.

For exact-count criteria, the project may instead choose exact-match scoring (100 for a match, 0 otherwise). The project lead must choose and document one approach consistently before implementation.

This formula is a proposed baseline, not an already-approved final scoring policy. The project lead must approve the tolerance and scoring approach for each criterion.

## 5. Overall score

The overall score is a weighted average:

`overall_score = sum(weight_i * parameter_score_i) / sum(weight_i)`

Weights must be non-negative. Only enabled criteria are included. At least one criterion must be enabled and the sum of included weights must be greater than zero.

If weights are configured as fractions, they should sum to 1. If configured as arbitrary positive values, divide by their sum as shown above.

Round the displayed overall score consistently (recommended: two decimal places). Keep sufficient precision internally.

## 6. Missing and invalid values

- Required parameters missing from the request should fail validation.
- Negative volume, surface area, or bounding-box dimensions should fail validation.
- Counts must be non-negative integers.
- Center-of-mass coordinates may be negative if the question's coordinate frame allows them.
- Unknown face-type keys should either be rejected or mapped to `other` according to one documented backend rule. Do not handle them inconsistently.
- Do not silently replace invalid values with zero.

## 7. Special cases

- If expected scalar value is zero, use a configured absolute tolerance rather than percentage error.
- If a parameter is not relevant to a question, mark it disabled in the question configuration and exclude it from the overall score.
- If an expected parameter is absent, do not assume it is zero unless the question definition explicitly says so.
- For topology-based values (face and edge counts), consider CAD-kernel differences when setting tolerances.
- A high score does not prove geometric identity. Multiple different solids can share similar mass properties and topology counts.

## 8. Moment of inertia — blocked pending a decision

Do not implement scoring for moment of inertia until the project lead approves its definition and representation. A 3D mass moment of inertia is generally represented by a tensor, not one arbitrary scalar. The team must decide the physical quantity, reference point, axes, units, density assumptions, and API representation first.

## 9. Configuration required per question

Before a question is released, its backend configuration should specify:
- expected parameter values;
- enabled/disabled criteria;
- comparison method for each criterion;
- tolerance for each criterion;
- weight for each criterion;
- coordinate frame and axis order;
- moment-of-inertia convention, if that criterion is enabled;
- supported face-type classification rules.

Do not hardcode one global tolerance or weight for every question unless the project lead explicitly approves that design.
