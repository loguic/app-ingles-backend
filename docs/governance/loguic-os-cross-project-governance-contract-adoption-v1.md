# LOGUIC English — LOGUIC OS Cross-Project Governance Contract v1 Adoption

## Adoption declaration

| Field | Value |
| --- | --- |
| `project_id` | `LOGUIC-English` |
| `policy_contract_id` | `LOGUIC-OS-CROSS-PROJECT-GOVERNANCE-CONTRACT` |
| `adopted_version` | `1.0.0` |
| `available_version` | `1.0.0` |
| `exact_identity` | `LOGUIC-OS-CROSS-PROJECT-GOVERNANCE-CONTRACT@1.0.0` |
| `adoption_state` | `ADOPTED` |
| `authority` | `Human Authority` |
| `upstream_authority` | `LOGUIC OS` |
| `upstream_human_gate` | `HG-P1-GOV-001-V1` |
| `upstream_source_commit` | `a0bc49b2cc6eb27d25cfa8361febd97aefb36844` |
| `upstream_source_file` | `docs/governance/P1-GOV-001-cross-project-governance-versioned-policy-contract-v1.md` in the LOGUIC OS repository |
| `upstream_contract_status` | `APPROVED / MATERIALIZED / AVAILABLE` |
| `upstream_publication_state` | `COMMITTED_LOCAL / PENDING_REMOTE_CONFIGURATION` |
| `compatibility` | `COMPATIBLE` |
| `migration_required` | `NO` |
| `supersession` | `NONE OBSERVED FOR ADOPTED VERSION` |

The authoritative upstream file was verified read-only from the pinned commit before this declaration was created. In that file, policy status is `APPROVED`, materialization is closed in the committed Git object, adoption availability is `AVAILABLE`, and the approved identity is exactly `LOGUIC-OS-CROSS-PROJECT-GOVERNANCE-CONTRACT@1.0.0`. The absence of an upstream LOGUIC OS remote does not invalidate that locally materialized authority.

## Adopted governance effect

LOGUIC English adopts exactly version `1.0.0` for cross-project governance. This adoption establishes:

- explicit, versioned cross-project authority and explicit project adoption;
- no silent policy migration and no transitive authority;
- fail-closed behavior for the affected integration when required policy authority is missing, ambiguous, incompatible, contradictory, unavailable, or version-indeterminate;
- separation between project evidence and global authority: project evidence alone cannot modify LOGUIC OS policy;
- global policy change only through LOGUIC OS governance and the applicable Human Gate; and
- preservation of project sovereignty outside the expressly adopted integration scope.

Failure is localized to the affected integration. It does not silently stop unrelated LOGUIC English operation or transfer control of project internals to LOGUIC OS.

## LOGUIC English sovereignty

LOGUIC English retains authority over its project-owned domain, including:

- pedagogical model;
- curriculum;
- learning content;
- teaching methodology within project-owned boundaries;
- product behavior; and
- runtime and domain implementation.

This adoption does not grant LOGUIC OS automatic authority over those domains. Any additional authority requires an explicit, scoped, governed decision.

## Version, migration, and policy-import boundary

For this adoption:

- `CURRENT VERSION = 1.0.0`;
- `AVAILABLE VERSION = 1.0.0`;
- `MIGRATION REQUIRED = NO`.

No future `1.x`, `2.x`, or superseding contract is adopted automatically. Publication, availability, chronology, a repository HEAD, or a `latest` convention cannot change the pinned adopted version. Every future migration remains an explicit governed decision with its own compatibility assessment and applicable Human Gate.

This declaration does not automatically import every current LOGUIC OS operational practice. Prompt task titles, specific Git closure practices, operational retrospective rules, Operational Resilience, and other shared engineering policies require their own explicit versioned authority or governed project-contract decision when cross-project adoption is needed. Operational Resilience is not implemented or adopted here.

## Cross-project feedback

Future material engineering observations from LOGUIC English may be raised to LOGUIC OS as:

- evidence;
- finding;
- proposal;
- friction;
- contradiction; or
- candidate reusable mechanism.

Such feedback preserves provenance and the distinction between observation and proposal. Submission, recurrence, implementation success, or upstream classification does not itself modify LOGUIC OS authority.

## Preserved project frontiers

This governance microblock is separate from Token Reduction. Increments 1, 2, and 3 remain `CLOSED / PUBLISHED / SYNCED`; no Increment 4 is created.

Functional objective B is not begun by this adoption. After this governance adoption is completely closed, B may return as the functional next objective unless another explicitly governed dependency supersedes it.

This adoption does not reactivate or change A1, B52, the loader, B181, human review, adjudication, or winner state. It creates no runtime, curriculum, content, persistence, migration, API, or product-behavior change.

## Closure boundary

The Human Authority decision makes the exact adoption state `ADOPTED`. Repository implementation, deterministic validation, postflight, and Git closure remain distinct evidence. This record must not be interpreted as a commit, push, remote publication, or automatic authorization to begin functional objective B.
