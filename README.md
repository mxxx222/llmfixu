# Flipper Analyzer

This Python project provides tools for analyzing Flipper Zero `.sub` files. It includes utilities for reading, decoding, classifying signals, and visualizing data.

## Features
- Parse `.sub` files to extract signal data.
- Classify signals as fixed or rolling codes.
- Detect protocols used in the signal.
- Visualize signal data with matplotlib.

## Project Structure
```
flipper-analyzer/
├── main.py
├── analyzers/
│   ├── reader.py      # Reads .sub files
│   ├── decoder.py     # Thresholding and binary decoding
│   ├── protocol.py    # Protocol detection
│   └── classifier.py  # Rolling vs fixed classification
├── utils/
│   └── plotter.py     # Visualization tools
├── examples/
│   └── sample1.sub    # Example .sub file
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.11+
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### Usage
Run the main script to analyze an example `.sub` file:
```bash
python main.py
```

## Example Output
```
Analyysi: Fixed Code
Signal visualized in plot.png
```

## Contributing
Feel free to submit issues or pull requests to improve this project.