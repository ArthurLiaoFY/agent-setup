# Agent Setup - Final Test Gap Closure

## Result

The focused resource failure tests requested by GPT were added. No installer architecture,
directory layout, ownership policy, or runtime dependency was changed.

## Added Coverage

| Scenario | Test | Target State Assertion |
|---|---|---|
| Missing selected Adapter | `test_missing_adapter_resource_does_not_modify_target` | Target directory remains absent |
| Missing CORE | `test_missing_core_resource_does_not_modify_target` | Target directory remains absent |
| Missing Fundamental file | `test_missing_fundamental_resource_does_not_modify_existing_target` | Existing sentinel remains unchanged |
| Missing Additional file | `test_missing_additional_resource_does_not_modify_existing_target` | Existing sentinel remains unchanged |
| Resource read failure | `test_resource_read_failure_does_not_modify_target` | Target directory remains absent |

All five resource failure tests assert that `InstallError` is raised.

## Target Modification Guarantee

The tests cover both required target states:

- A non-existent target remains non-existent when package validation/read failures occur.
- An existing target retains its sentinel content when a packaged resource is missing.

These assertions verify that failures occur before `target.mkdir()` and before the installation
write loop.

## Existing API Coverage

`test_install_accepts_string_target` verifies that `install()` accepts a string target.
The existing installer tests also cover `Path` targets.

## Adapter Coverage

The following adapter tests remain present:

- Claude uses `@agent_rules/CORE.md`.
- Codex explicitly instructs the Agent to read `agent_rules/CORE.md`.
- Copilot explicitly instructs the Agent to read `agent_rules/CORE.md`.

## Verification

Complete test suite:

```text
32 passed in 0.10s
```

Wheel verification:

```bash
uv build
```

The wheel and source distribution were rebuilt successfully. The packaged adapters, CORE,
Fundamental rules, and Additional rules were confirmed in the wheel.

Git verification:

```text
git diff --check: PASS
```

## Final Assessment

Phase 1's test gap for resource validation and read failures is closed. The installation is
verified not to create or modify target content when simulated package resources fail before
execution. Actual filesystem write failures can still occur after writes begin, as documented
by the non-transactional installer design.
