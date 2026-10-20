# Defect review before changing code

The eleven complete prior failure/error tracebacks are recorded in
`failure_diagnosis.json`. The acquisition subprocess was reproduced without
changing its assertions; its stderr proves that the hardcoded helper path was
absent and that checksum validation did not execute in that subprocess.

The native Windows dataset inventory has a genuine metadata portability defect:
it compares `str(Path.relative_to(...))` strings with POSIX paths from the VisA
CSV. The traceback lists each fixture twice under different separators. An
explicit POSIX relative-path serialization would be the appropriate Windows
portability correction. No numerical anomaly-scoring defect is implicated.

The repository's declared runtime is Linux/Python 3.12 (`framework/pyproject.toml`
requires >=3.12,<3.13), and the recorded protocol used Python 3.12.14 and Torch
2.7.1+cpu. The retained startup instructions require `/workspace/tools`; the
current framework tests explicitly depend on that layout, `/tmp`, symlinks and
POSIX `fcntl`. The previous native Windows runtime was outside that contract.

Repair strategy: provision the declared Linux runtime with the documented layout,
exact declared numerical/dependency versions and UTF-8 encoding. Run both existing
test suites unchanged with the same interpreter. This addresses the observed
platform/dependency failures without editing model code or weakening tests.

No source/test assertion changes have been made. If the unchanged suites fail in
the compatible runtime, record the new complete traceback and document a separate
defect before changing implementation. The only proposed file outside the new
evidence directory is a repair-only GitHub Actions runtime definition; it contains
no smoke inference, source selection or target-evaluation command.
