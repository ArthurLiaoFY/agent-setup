# Agent Setup — Final Test Gap Closure

The Phase 1 implementation is considered functionally complete.

Before closing Phase 1, perform a focused test-only verification of resource failure handling.

## Required Tests

1. Missing selected adapter resource.
2. Missing CORE resource.
3. Missing individual Fundamental resource.
4. Missing individual Additional resource.
5. Resource read failure.
6. Verify that every failure above occurs before target project modification.
7. Verify `install()` accepts both `str` and `Path`.

## Important Assertions

For resource validation and read failures:

- The installer raises `InstallError`.
- No target files are created or overwritten.
- If the target project already exists, its contents remain unchanged.
- Ideally, verify that the target directory is not created when it did not previously exist.

Use monkeypatched package resources where appropriate to simulate missing or unreadable resources.

## Constraints

- Do not redesign the installer.
- Do not change the directory structure.
- Do not introduce manifest, rollback, transaction, or new dependencies.
- Do not change the established ownership policy.
- Do not modify unrelated files.

## Final Verification

Run the complete test suite and report:

- Test results.
- Whether each required failure scenario is covered.
- Whether target state remains unchanged after each simulated failure.

No additional feature work is required.