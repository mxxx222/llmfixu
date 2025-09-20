"""
Flipper Zero .sub file reader module
Parses .sub files and extracts raw signal data
"""

import re
from typing import Dict, List, Tuple, Optional


class SubFileData:
    """Container for parsed .sub file data"""
    
    def __init__(self):
        self.filetype: str = ""
        self.version: int = 0
        self.frequency: int = 0
        self.preset: str = ""
        self.protocol: str = ""
        self.key: str = ""
        self.raw_data: List[int] = []
        self.raw_pulses: List[int] = []


def parse_sub_file(filepath: str) -> SubFileData:
    """
    Parse a Flipper Zero .sub file and extract signal data
    
    Args:
        filepath: Path to the .sub file
        
    Returns:
        SubFileData object containing parsed data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is invalid
    """
    data = SubFileData()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Sub file not found: {filepath}")
    
    # Parse header fields
    for line in content.split('\n'):
        line = line.strip()
        
        if line.startswith('Filetype:'):
            data.filetype = line.split(':', 1)[1].strip()
        elif line.startswith('Version:'):
            data.version = int(line.split(':', 1)[1].strip())
        elif line.startswith('Frequency:'):
            data.frequency = int(line.split(':', 1)[1].strip())
        elif line.startswith('Preset:'):
            data.preset = line.split(':', 1)[1].strip()
        elif line.startswith('Protocol:'):
            data.protocol = line.split(':', 1)[1].strip()
        elif line.startswith('Key:'):
            data.key = line.split(':', 1)[1].strip()
        elif line.startswith('RAW_Data:'):
            # Parse raw pulse data
            raw_line = line.split(':', 1)[1].strip()
            data.raw_data = [int(x) for x in raw_line.split() if x.isdigit() or (x.startswith('-') and x[1:].isdigit())]
    
    # Process raw data into pulse durations
    data.raw_pulses = _process_raw_data(data.raw_data)
    
    if not data.raw_data and not data.key:
        raise ValueError("No valid signal data found in file")
    
    return data


def _process_raw_data(raw_data: List[int]) -> List[int]:
    """
    Process raw pulse data from .sub file
    
    Args:
        raw_data: List of raw timing values
        
    Returns:
        List of pulse durations
    """
    if not raw_data:
        return []
    
    # Convert to absolute values and filter out obviously invalid data
    pulses = [abs(x) for x in raw_data if abs(x) > 0]
    
    return pulses


def get_signal_stats(data: SubFileData) -> Dict[str, any]:
    """
    Get basic statistics about the signal
    
    Args:
        data: Parsed sub file data
        
    Returns:
        Dictionary with signal statistics
    """
    if not data.raw_pulses:
        return {}
    
    stats = {
        'total_pulses': len(data.raw_pulses),
        'min_pulse': min(data.raw_pulses),
        'max_pulse': max(data.raw_pulses),
        'avg_pulse': sum(data.raw_pulses) / len(data.raw_pulses),
        'frequency': data.frequency,
        'protocol': data.protocol,
        'duration_ms': sum(data.raw_pulses) / 1000  # Convert to milliseconds
    }
    
    return stats


def extract_raw_signal(data: SubFileData) -> List[Tuple[int, int]]:
    """
    Extract raw signal as (duration, level) pairs
    
    Args:
        data: Parsed sub file data
        
    Returns:
        List of (duration, level) tuples where level alternates between 1 and 0
    """
    if not data.raw_pulses:
        return []
    
    signal = []
    level = 1  # Start with high
    
    for duration in data.raw_pulses:
        signal.append((duration, level))
        level = 1 - level  # Alternate between 1 and 0
    
    return signal