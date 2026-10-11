"""Fail fast when generated files or legacy entry points leak into source folders."""

from __future__ import annotations

import subprocess
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = (
    "docs/README.md",
    "docs/architecture/README.md",
    "docs/architecture/frontend.md",
    "docs/architecture/backend.md",
    "docs/architecture/network-security.md",
    "docs/architecture/data-and-storage.md",
    "docs/development/local-setup.md",
    "docs/deployment/README.md",
    "docs/operations/release-checklist.md",
    "docs/product/README.md",
    "docs/3d/README.md",
    "docs/planning/README.md",
    "docs/audits/README.md",
    "docs/archive/README.md",
    "ecommerce/backend/app/cli",
    "scripts",
    "tools/catalog",
)

LEGACY_ENTRY_POINTS = (
    "scraper.py",
    "diy_parts.py",
    "ecommerce/backend/scripts/import_price_verification.py",
    "docs/website.md",
    "docs/team-work-plan.md",
    "docs/3d-asset-pipeline.md",
    "docs/3d-pc-builder-plan.md",
    "docs/commercial-readiness-2026-07-17.md",
    "docs/demo-script.md",
    "docs/diy-parts.md",
    "docs/full-stack-audit.md",
    "docs/offline-store-photo-checklist.md",
    "docs/products.md",
    "docs/project-optimization-plan.md",
    "docs/service-agreements.md",
    "docs/supabase-deployment.md",
    "docs/tech-stack-optimization.md",
    "ecommerce/docs/architecture.md",
    "ecommerce/docs/setup.md",
    "ecommerce/docs/checklist.md",
)

GENERATED_PARTS = {
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".vite",
    "dist",
    "node_modules",
}


def tracked_existing_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
    )
    return [
        REPOSITORY_ROOT / entry.decode("utf-8")
        for entry in result.stdout.split(b"\0")
        if entry and (REPOSITORY_ROOT / entry.decode("utf-8")).is_file()
    ]


def main() -> int:
    problems: list[str] = []

    for relative_path in REQUIRED_PATHS:
        if not (REPOSITORY_ROOT / relative_path).exists():
            problems.append(f"缺少目录约定中的必需路径：{relative_path}")

    docs_root = REPOSITORY_ROOT / "docs"
    for path in docs_root.glob("*.md"):
        if path.name != "README.md":
            problems.append(
                f"docs 根目录只允许 README.md，请把文档归入职责目录：{path.relative_to(REPOSITORY_ROOT).as_posix()}"
            )

    for relative_path in LEGACY_ENTRY_POINTS:
        if (REPOSITORY_ROOT / relative_path).exists():
            problems.append(f"旧入口应迁移到当前职责目录：{relative_path}")

    for path in tracked_existing_files():
        relative_path = path.relative_to(REPOSITORY_ROOT)
        if GENERATED_PARTS.intersection(relative_path.parts):
            problems.append(f"生成物不应进入版本控制：{relative_path.as_posix()}")

    if problems:
        print("Directory structure check failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("Directory structure check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
