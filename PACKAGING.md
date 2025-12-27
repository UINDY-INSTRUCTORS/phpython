# phpython - Lean Packaging Guide

## Package Structure

Your package is now set up for lean distribution with this structure:

```
phpython/
├── phpython/              # Package directory (importable)
│   ├── __init__.py        # Public API exports
│   ├── core.py            # Hardware classes (A, D, P, I2C)
│   ├── platforms.py       # Platform detection
│   └── utils.py           # Utility classes (Timer, DataLogger)
├── setup.py               # Build configuration
├── pyproject.toml         # PEP 517/518 build backend config
├── setup.cfg              # Package metadata
├── MANIFEST.in            # Distribution file inclusion rules
├── README.md              # User documentation
└── dist/                  # Built distributions (generated)
    └── phpython-0.1.0.tar.gz
```

## What's Excluded from Distribution

The following files are **NOT** included in the distribution to keep it lean:

- `examples.py` - Examples remain in source repo
- `test_phpython.py` - Tests remain in source repo
- `converted_projects/` - Reference materials
- `QUICKSTART.md`, `MIGRATION.md`, `INSTRUCTOR_GUIDE.md`, `INDEX.md` - Reference docs
- `__pycache__/`, `*.pyc` - Compiled files
- `.git/`, `.gitignore` - Git metadata

## Distribution Size

- **Source distribution (sdist)**: ~12 KB
- **Package code**: ~400 lines (core implementation only)
- **Dependencies**: None (uses only platform-native modules)

## How to Build Distributions

### Source distribution (tarball)
```bash
python setup.py sdist
# Output: dist/phpython-0.1.0.tar.gz
```

### Wheel distribution (faster install)
```bash
pip install wheel
python setup.py bdist_wheel
# Output: dist/phpython-0.1.0-py3-none-any.whl
```

### Modern build (requires setuptools)
```bash
pip install build
python -m build
# Output: dist/phpython-0.1.0.tar.gz and dist/phpython-0.1.0-*.whl
```

## Distribution Methods

### Method 1: Direct Download/Copy (Recommended for students)
Users download and copy the `phpython/` directory into their project:

```bash
# In their project
cp -r /path/to/phpython/phpython ./
from phpython import A, D, P
```

### Method 2: PyPI Installation (Optional)
To publish to PyPI:

```bash
pip install twine
python setup.py sdist bdist_wheel
twine upload dist/*
```

Then users can install with:
```bash
pip install phpython
```

### Method 3: Direct Installation from Source
```bash
pip install dist/phpython-0.1.0.tar.gz
# or
pip install git+https://github.com/yourusername/phpython.git
```

## Customizing the Package

### Change Version
Edit `setup.py`:
```python
version='0.2.0',
```

### Add author information
Edit `setup.py`:
```python
author='Your Name',
author_email='your.email@example.com',
```

### Add/remove dependencies
Edit `setup.py` (currently has no dependencies - keep it lean!):
```python
install_requires=[
    # 'some-package>=1.0',
],
```

### Update PyPI URLs
Edit `setup.py`:
```python
project.urls
Homepage = "https://github.com/yourusername/phpython"
```

## What Each File Does

| File | Purpose |
|------|---------|
| `setup.py` | Build configuration (backwards compatible) |
| `pyproject.toml` | Modern Python build specification (PEP 517/518) |
| `setup.cfg` | Alternative metadata storage (optional) |
| `MANIFEST.in` | Controls what gets included in distributions |

## Testing the Package

```bash
# Install from distribution
pip install dist/phpython-0.1.0.tar.gz

# Test imports
python3 -c "from phpython import A, D, P, I2C; print('✓ Works!')"

# Run tests from source (not in distribution)
python test_phpython.py
```

## Summary

- **Package size**: 12 KB (very lean)
- **No external dependencies**: Uses only Python stdlib + platform modules
- **Flexible distribution**: Works with copy-paste, pip, or PyPI
- **Student-friendly**: Simple, readable source code
- **Properly packaged**: Follows Python packaging standards

Your module is ready for distribution! 🎉
