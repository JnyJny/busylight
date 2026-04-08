#!/usr/bin/env python3
"""
Cross-package dependency verification for busylight monorepo.

This tool scans all imports in each workspace member and cross-references
against declared dependencies in pyproject.toml to prevent the monorepo
from silently devolving into a monolith by catching undeclared cross-package
dependencies.

Dispatch #68: Add prek dependency verification to busylight-core monorepo CI
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set

import tomllib


class ImportVisitor(ast.NodeVisitor):
    """Extract all imports from Python AST."""
    
    def __init__(self):
        self.imports: Set[str] = set()
    
    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            module_name = alias.name.split('.')[0]
            # Only add valid Python identifiers (avoid things like "busylight-core")
            if module_name.isidentifier():
                self.imports.add(module_name)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            # Skip relative imports (node.level > 0 indicates relative import)
            if node.level == 0:
                module_name = node.module.split('.')[0]
                # Only add valid Python identifiers
                if module_name.isidentifier():
                    self.imports.add(module_name)


def get_workspace_packages(root_path: Path) -> Dict[str, Dict]:
    """Get all workspace packages and their metadata."""
    root_pyproject = root_path / "pyproject.toml"
    if not root_pyproject.exists():
        raise FileNotFoundError(f"Root pyproject.toml not found at {root_pyproject}")
    
    with open(root_pyproject, 'rb') as f:
        root_config = tomllib.load(f)
    
    workspace_members = root_config.get("tool", {}).get("uv", {}).get("workspace", {}).get("members", [])
    
    packages = {}
    for member_pattern in workspace_members:
        member_dirs = root_path.glob(member_pattern)
        for member_dir in member_dirs:
            if member_dir.is_dir():
                pyproject_path = member_dir / "pyproject.toml"
                if pyproject_path.exists():
                    with open(pyproject_path, 'rb') as f:
                        config = tomllib.load(f)
                    
                    project_name = config.get("project", {}).get("name", "")
                    if project_name:
                        # Determine the actual module name by checking src structure
                        module_name = project_name.replace("-", "_")
                        
                        # Check if there's a src directory structure
                        src_path = member_dir / "src"
                        if src_path.exists():
                            # Find the actual module directory under src
                            for item in src_path.iterdir():
                                if item.is_dir() and not item.name.startswith('.'):
                                    module_name = item.name
                                    break
                        
                        packages[project_name] = {
                            "path": member_dir,
                            "config": config,
                            "module_name": module_name
                        }
    
    return packages


def extract_imports_from_file(file_path: Path) -> Set[str]:
    """Extract all top-level imports from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        visitor = ImportVisitor()
        visitor.visit(tree)
        return visitor.imports
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Warning: Could not parse {file_path}: {e}")
        return set()


def get_package_imports(package_path: Path) -> Set[str]:
    """Get all imports from all Python files in a package."""
    imports = set()
    
    # Scan src directory if it exists, otherwise scan the package directory
    src_path = package_path / "src"
    scan_path = src_path if src_path.exists() else package_path
    
    for py_file in scan_path.rglob("*.py"):
        # Skip __pycache__ and test files
        if "__pycache__" in str(py_file) or "tests/" in str(py_file):
            continue
            
        file_imports = extract_imports_from_file(py_file)
        imports.update(file_imports)
    
    return imports


def get_declared_dependencies(config: Dict) -> Set[str]:
    """Extract declared dependencies from pyproject.toml config."""
    dependencies = set()
    
    # Get main dependencies
    deps = config.get("project", {}).get("dependencies", [])
    for dep in deps:
        # Extract package name from dependency spec (e.g. "busylight-core>=2.3.0" -> "busylight-core")
        dep_name = dep.split(">=")[0].split("==")[0].split("~=")[0].split("<")[0].split(">")[0].strip()
        dependencies.add(dep_name)
    
    return dependencies


def check_cross_package_dependencies(packages: Dict[str, Dict]) -> List[str]:
    """Check for undeclared cross-package dependencies."""
    issues = []
    
    # Create a mapping of module names to package names
    module_to_package = {info["module_name"]: name for name, info in packages.items()}
    
    for package_name, package_info in packages.items():
        print(f"Checking {package_name}...")
        
        # Get all imports used by this package
        package_imports = get_package_imports(package_info["path"])
        
        # Get declared dependencies
        declared_deps = get_declared_dependencies(package_info["config"])
        
        # Check for cross-package imports
        for imported_module in package_imports:
            if imported_module in module_to_package:
                # This is a cross-package import
                target_package = module_to_package[imported_module]
                
                # Skip self-imports
                if target_package == package_name:
                    continue
                
                # Check if this cross-package dependency is declared
                # Handle both the declared package name and normalized module name
                target_package_normalized = target_package.replace("_", "-")
                if target_package not in declared_deps and target_package_normalized not in declared_deps:
                    issues.append(
                        f"{package_name}: imports '{imported_module}' from package '{target_package}' "
                        f"but '{target_package}' (or '{target_package_normalized}') is not declared in dependencies"
                    )
    
    return issues


def main():
    """Main entry point."""
    root_path = Path.cwd()
    
    try:
        packages = get_workspace_packages(root_path)
        print(f"Found {len(packages)} workspace packages:")
        for name, info in packages.items():
            print(f"  - {name} (module: {info['module_name']})")
        print()
        
        issues = check_cross_package_dependencies(packages)
        
        if issues:
            print("❌ Found undeclared cross-package dependencies:")
            print("   These imports violate monorepo dependency boundaries:")
            print()
            for issue in issues:
                print(f"  • {issue}")
            print("\n💡 To fix these issues:")
            print("   1. Add the missing dependencies to the appropriate pyproject.toml")
            print("   2. Or refactor the code to avoid the cross-package import")
            print("   3. This prevents the monorepo from becoming a monolith")
            print(f"\nTotal issues: {len(issues)}")
            sys.exit(1)
        else:
            print("✅ All cross-package dependencies are properly declared!")
            print("   Monorepo dependency boundaries are maintained.")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()