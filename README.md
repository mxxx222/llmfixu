# Flipper Zero .sub File Analyzer

A comprehensive Python project for analyzing Flipper Zero .sub files, featuring signal decoding, protocol identification, and rolling vs fixed code classification.

## Project Structure

```
flipper-analyzer/
├── main.py                 # Main entry point and CLI interface
├── analyzers/              # Analysis modules
│   ├── __init__.py
│   ├── reader.py          # .sub file parsing and data extraction
│   ├── decoder.py         # Signal thresholding and binary decoding
│   ├── protocol.py        # Protocol identification and analysis
│   └── classifier.py      # Rolling vs fixed code classification
├── utils/                  # Utility modules
│   ├── __init__.py
│   └── plotter.py         # Matplotlib visualizations
├── examples/               # Example data
│   └── sample1.sub        # Sample .sub file for testing
└── README.md              # This file
```

## Features

- **Signal Analysis**: Parse and analyze Flipper Zero .sub files
- **Protocol Identification**: Identify common RF protocols (KeeLoq, Princeton, CAME, etc.)
- **Signal Classification**: Classify signals as rolling code or fixed code
- **Multiple Decoders**: Support for OOK, PWM, and Manchester encoding
- **Visualizations**: Generate comprehensive plots and analysis reports
- **Comparison Tools**: Compare multiple signals for device identification

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mxxx222/llmfixu.git
   cd llmfixu
   ```

2. **Install dependencies:**
   ```bash
   pip install matplotlib numpy
   ```

## Usage

### Basic Usage

```python
from flipper-analyzer.analyzers.reader import parse_sub_file
from flipper-analyzer.analyzers.classifier import classify_signal
from flipper-analyzer.utils.plotter import plot_signal

# Parse a .sub file
signal = parse_sub_file("examples/sample1.sub")

# Classify the signal
classification = classify_signal(signal)
print("Signal Type:", classification.signal_type)
print("Confidence:", f"{classification.confidence:.2%}")

# Visualize the signal
plot_signal(signal)
```

### Command Line Interface

Navigate to the `flipper-analyzer` directory first:
```bash
cd flipper-analyzer
```

**Analyze a single file:**
```bash
python main.py examples/sample1.sub
```

**Compare two files:**
```bash
python main.py --compare file1.sub file2.sub
```

**Save analysis output:**
```bash
python main.py examples/sample1.sub --save
```

**Run example analysis:**
```bash
python main.py --example
```

**Disable plots (for headless environments):**
```bash
python main.py examples/sample1.sub --no-plots
```

### Advanced Usage

**Protocol identification:**
```python
from flipper-analyzer.analyzers.protocol import identify_protocol, extract_protocol_fields

# Identify protocol
protocol_info = identify_protocol(signal)
print("Protocol:", protocol_info['identified_protocol'])

# Extract protocol-specific fields
fields = extract_protocol_fields(signal, protocol_info['identified_protocol'])
print("Fields:", fields['fields'])
```

**Signal comparison:**
```python
from flipper-analyzer.analyzers.classifier import compare_signals

signal1 = parse_sub_file("signal1.sub")
signal2 = parse_sub_file("signal2.sub")

comparison = compare_signals(signal1, signal2)
print("Same device probability:", f"{comparison['same_device_probability']:.2%}")
```

**Generate analysis report:**
```python
from flipper-analyzer.utils.plotter import save_analysis_report

save_analysis_report(signal, classification, "output_directory")
```

## Supported Protocols

The analyzer can identify and analyze the following protocols:

- **KeeLoq** - Rolling code protocol used in car remotes
- **HCS301/HCS200** - Microchip rolling code protocols
- **Princeton** - PT2262/PT2272 fixed code protocol
- **CAME** - Gate remote protocol
- **Nice FLO** - Nice gate protocol
- **Chamberlain** - Garage door opener protocol
- **Linear** - Linear garage door protocol
- **FAAC SLH** - FAAC rolling code protocol

## Analysis Features

### Signal Characteristics
- Frequency analysis
- Pulse duration statistics
- Signal complexity scoring
- Entropy analysis
- Pattern repetition detection

### Classification Criteria
- **Rolling Code Indicators:**
  - Long bit length (>64 bits)
  - Complex encoding (PWM/Manchester)
  - High signal entropy
  - Low pattern repetition
  - Known rolling code protocols

- **Fixed Code Indicators:**
  - Short bit length (<40 bits)
  - Simple encoding (OOK)
  - Low signal entropy
  - High pattern repetition
  - Known fixed code protocols

### Visualization Options
- Raw pulse duration plots
- Time domain signal visualization
- Binary signal after thresholding
- Frequency spectrum analysis
- Classification confidence charts
- Protocol match confidence
- Signal comparison plots

## File Format Support

The analyzer supports standard Flipper Zero .sub file format:

```
Filetype: Flipper SubGhz RAW File
Version: 1
Frequency: 433920000
Preset: FuriHalSubGhzPresetOok650Async
Protocol: RAW
RAW_Data: 4500 -1500 450 -450 450 -1350 ...
```

## Example Output

```
Analyzing file: examples/sample1.sub
==================================================
✓ File parsed successfully

Signal Statistics:
  total_pulses: 66
  min_pulse: 450
  max_pulse: 4500
  avg_pulse: 808.33
  frequency: 433920000
  protocol: RAW
  duration_ms: 53.35

Signal Type: Fixed
Confidence: 78%

Analysis:
  • Protocol Princeton is typically a fixed code protocol
  • Shorter bit length suggests fixed code
  • Simple encoding (OOK) often used in fixed codes
  • Low pattern repetition suggests fixed code

Identified Protocol: Princeton
Protocol Confidence: 75%

Protocol Fields (Princeton):
  address: 1010101010110011
  data: 1001
  Interpretation: Fixed code with device ID and button pattern

Decoded Data:
  Hex: AB349
  Encoding: ook
  Bits: 20
```

## Requirements

- Python 3.7+
- matplotlib (for visualizations)
- numpy (for signal processing)

## Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.

## License

This project is open source and available under the [MIT License](LICENSE).