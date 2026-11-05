# 1. Overview

This plan implements the optimization recommendations for the agent-setup package.

# 2. Scope

The implementation includes resource manifests.
The implementation includes plan and lesson commands.
The implementation includes status and uninstall commands.
The implementation includes initial Additional directories.
The implementation includes focused tests.

# 3. Investigation

The installer uses hard-coded resource groups and destinations.
The CLI creates target directories before resource validation.
The project has no lifecycle commands for status or uninstall.
Plan and lesson files receive sequence numbers only through Agent instructions.

# 4. Proposed Approach

Create a manifest module for ownership and destinations.
Use the manifest in installer path construction.
Create plan and lesson commands with sequential filenames.
Create status and uninstall commands.
Create Additional directories during installation.
Keep existing user-owned files.

# 5. Implementation Steps

1. Add the manifest module.
2. Remove duplicated path ownership data from the installer.
3. Add plan and lesson filename utilities.
4. Add plan, lesson, status, and uninstall CLI commands.
5. Move target directory creation into installer execution.
6. Add tests for manifests, numbering, directories, status, and uninstall.
7. Run the focused test suite.
8. Run packaging validation.

# 6. Testing and Verification

Run the Python test suite.
Run git diff validation.
Run the package build.
Verify the installed directories remain available.
Verify status identifies managed and user files.
Verify uninstall removes only installer-managed files.

# 7. Risks and Open Questions

Uninstall requires an installed-file inventory.
The package currently has no persistent installation manifest in targets.
This implementation stores a local manifest in `.agent_rules/manifest.json`.
This file uses installer-owned resources.

# 8. Completion Criteria

All resource destinations come from the manifest.
Plan and lesson names use the next sequential number.
Status reports the installation state.
Uninstall removes files that the installer owns.
The full focused test suite passes.
The package builds successfully.

# 9. Execution Summary

Implementation is complete.
