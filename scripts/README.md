# Scripts

## Cross-Package Dependency Verification

### `verify-cross-package-deps.py` (Dispatch #68)

This script implements cross-package dependency verification to prevent the monorepo from silently devolving into a monolith by catching undeclared cross-package dependencies.

#### Purpose

In a monorepo, it's easy for packages to accidentally import from other packages without declaring them as proper dependencies. This creates hidden coupling and defeats the purpose of having separate packages. The verification script ensures that:

1. All cross-package imports are explicitly declared in `pyproject.toml` dependencies
2. No undeclared cross-package dependencies exist
3. The monorepo maintains proper dependency boundaries

#### How it works

1. **Discovery**: Scans all workspace members defined in the root `pyproject.toml`
2. **Import Analysis**: Uses Python's AST to extract all imports from each package's source files
3. **Cross-Reference**: Matches imports against declared dependencies in each package's `pyproject.toml`
4. **Validation**: Reports any cross-package imports that lack corresponding dependency declarations

#### Usage

```bash
# Run from monorepo root
uv run python scripts/verify-cross-package-deps.py
```

#### CI Integration

The script is integrated into the CI workflow as part of the `dependency-check` job. It runs on every PR and push to catch dependency boundary violations early.

#### Example Output

**Success:**
```
Found 2 workspace packages:
  - busylight-for-humans (module: busylight)
  - busylight_core (module: busylight_core)

Checking busylight-for-humans...
Checking busylight_core...
✅ All cross-package dependencies are properly declared!
   Monorepo dependency boundaries are maintained.
```

**Failure:**
```
❌ Found undeclared cross-package dependencies:
   These imports violate monorepo dependency boundaries:

  • busylight_core: imports 'busylight' from package 'busylight-for-humans' 
    but 'busylight-for-humans' is not declared in dependencies

💡 To fix these issues:
   1. Add the missing dependencies to the appropriate pyproject.toml
   2. Or refactor the code to avoid the cross-package import
   3. This prevents the monorepo from becoming a monolith

Total issues: 1
```

#### Technical Details

- **AST Parsing**: Uses Python's `ast` module to accurately parse import statements
- **Relative Import Handling**: Correctly ignores relative imports (`.module`) within packages
- **Dependency Mapping**: Handles both package names (`busylight-core`) and module names (`busylight_core`)
- **Workspace Detection**: Automatically discovers packages via uv workspace configuration

#### Relationship to existing tools

This complements the existing `deptry` checks by focusing specifically on cross-package boundaries within the monorepo, while `deptry` focuses on external dependencies.