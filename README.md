# Nitrix - A TUI Matrix client

Nitrix is a terminal user interface (TUI) Matrix client written in Python using [Textual](https://github.com/Textualize/textual) and the [matrix-nio](https://github.com/matrix-nio/matrix-nio) library.

## Installation

Nitrix can be installed using pip:

```bash
# Create a virtual environment
python3 -m venv nitrix_venv
source nitrix_venv/bin/activate

# Install Nitrix
pip install git+https://github.com/ThomasJRyan/Nitrix
```

And run using:

```bash
nitrix
```

## Development

To install Nitrix for development, clone the repository and install the dependencies:

```bash
git clone git@github.com:ThomasJRyan/Nitrix.git
cd Nitrix
pip install -e .
pip install -r requirements-dev.txt
```

When developing, you can run Nitrix using:

```bash
cd src/nitrix
textual run --dev app.py
```