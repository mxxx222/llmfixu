"""
Signal decoder module for Flipper Zero .sub files
Handles thresholding and binary conversion of RF signals
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from .reader import SubFileData


def apply_threshold(pulses: List[int], threshold_method: str = 'median') -> List[Tuple[int, int]]:
    """
    Apply thresholding to convert pulse durations to binary levels
    
    Args:
        pulses: List of pulse durations
        threshold_method: Method for determining threshold ('median', 'mean', 'adaptive')
        
    Returns:
        List of (duration, binary_level) tuples
    """
    if not pulses:
        return []
    
    # Calculate threshold based on method
    if threshold_method == 'median':
        threshold = np.median(pulses)
    elif threshold_method == 'mean':
        threshold = np.mean(pulses)
    elif threshold_method == 'adaptive':
        # Use adaptive threshold based on distribution
        q25, q75 = np.percentile(pulses, [25, 75])
        threshold = (q25 + q75) / 2
    else:
        threshold = np.median(pulses)  # Default fallback
    
    # Apply threshold
    binary_signal = []
    level = 1  # Start with high
    
    for duration in pulses:
        # Determine if this is a long (1) or short (0) pulse
        binary_level = 1 if duration > threshold else 0
        binary_signal.append((duration, binary_level))
        level = 1 - level  # Alternate for next pulse
    
    return binary_signal


def decode_manchester(signal: List[Tuple[int, int]]) -> List[int]:
    """
    Decode Manchester encoded signal
    Manchester encoding: 1 = high-to-low transition, 0 = low-to-high transition
    
    Args:
        signal: List of (duration, level) tuples
        
    Returns:
        List of decoded bits
    """
    if len(signal) < 2:
        return []
    
    bits = []
    i = 0
    
    while i < len(signal) - 1:
        current_level = signal[i][1]
        next_level = signal[i + 1][1]
        
        # Manchester encoding detection
        if current_level == 1 and next_level == 0:
            bits.append(1)  # High-to-low = 1
        elif current_level == 0 and next_level == 1:
            bits.append(0)  # Low-to-high = 0
        
        i += 2  # Skip to next bit pair
    
    return bits


def decode_ook(signal: List[Tuple[int, int]], short_threshold: int = None) -> List[int]:
    """
    Decode On-Off Keying (OOK) signal
    
    Args:
        signal: List of (duration, level) tuples
        short_threshold: Threshold for distinguishing short/long pulses
        
    Returns:
        List of decoded bits
    """
    if not signal:
        return []
    
    # Auto-determine threshold if not provided
    if short_threshold is None:
        durations = [duration for duration, _ in signal]
        short_threshold = np.median(durations)
    
    bits = []
    
    for duration, level in signal:
        if level == 1:  # Only consider high pulses
            if duration > short_threshold:
                bits.append(1)  # Long pulse = 1
            else:
                bits.append(0)  # Short pulse = 0
    
    return bits


def decode_pwm(signal: List[Tuple[int, int]]) -> List[int]:
    """
    Decode Pulse Width Modulation (PWM) signal
    
    Args:
        signal: List of (duration, level) tuples
        
    Returns:
        List of decoded bits
    """
    if not signal:
        return []
    
    # Extract high pulse durations
    high_pulses = [duration for duration, level in signal if level == 1]
    
    if not high_pulses:
        return []
    
    # Use median as threshold for PWM
    threshold = np.median(high_pulses)
    
    bits = []
    for duration, level in signal:
        if level == 1:  # Only decode high pulses
            bits.append(1 if duration > threshold else 0)
    
    return bits


def find_preamble(bits: List[int], preamble_pattern: List[int] = None) -> int:
    """
    Find preamble pattern in decoded bits
    
    Args:
        bits: List of decoded bits
        preamble_pattern: Expected preamble pattern (default: [1,0,1,0,1,0,1,0])
        
    Returns:
        Index of preamble start, -1 if not found
    """
    if preamble_pattern is None:
        preamble_pattern = [1, 0, 1, 0, 1, 0, 1, 0]  # Common alternating pattern
    
    if len(bits) < len(preamble_pattern):
        return -1
    
    for i in range(len(bits) - len(preamble_pattern) + 1):
        if bits[i:i + len(preamble_pattern)] == preamble_pattern:
            return i
    
    return -1


def extract_data_bits(bits: List[int], preamble_end: int, data_length: int = 24) -> List[int]:
    """
    Extract data bits after preamble
    
    Args:
        bits: List of decoded bits
        preamble_end: Index where preamble ends
        data_length: Expected length of data portion
        
    Returns:
        List of data bits
    """
    start_idx = preamble_end
    end_idx = min(start_idx + data_length, len(bits))
    
    return bits[start_idx:end_idx]


def bits_to_hex(bits: List[int]) -> str:
    """
    Convert bit list to hexadecimal string
    
    Args:
        bits: List of bits
        
    Returns:
        Hexadecimal string representation
    """
    if not bits:
        return ""
    
    # Pad to multiple of 4 bits
    while len(bits) % 4 != 0:
        bits.append(0)
    
    hex_chars = []
    for i in range(0, len(bits), 4):
        nibble = bits[i:i+4]
        value = nibble[0] * 8 + nibble[1] * 4 + nibble[2] * 2 + nibble[3]
        hex_chars.append(format(value, 'X'))
    
    return ''.join(hex_chars)


def decode_signal(data: SubFileData, encoding: str = 'auto') -> Dict[str, any]:
    """
    Main signal decoding function
    
    Args:
        data: Parsed sub file data
        encoding: Encoding type ('manchester', 'ook', 'pwm', 'auto')
        
    Returns:
        Dictionary with decoded signal information
    """
    if not data.raw_pulses:
        return {}
    
    # Apply thresholding
    binary_signal = apply_threshold(data.raw_pulses)
    
    result = {
        'raw_pulses': len(data.raw_pulses),
        'binary_signal': binary_signal,
        'encoding': encoding,
        'bits': [],
        'hex_data': '',
        'preamble_found': False
    }
    
    # Try different encoding methods
    if encoding == 'auto':
        # Try OOK first (most common)
        ook_bits = decode_ook(binary_signal)
        manchester_bits = decode_manchester(binary_signal)
        pwm_bits = decode_pwm(binary_signal)
        
        # Select the one with most reasonable bit count
        candidates = [
            ('ook', ook_bits),
            ('manchester', manchester_bits),
            ('pwm', pwm_bits)
        ]
        
        # Choose the one with most bits that's also reasonable length
        best_encoding, best_bits = max(candidates, key=lambda x: len(x[1]) if 8 <= len(x[1]) <= 1000 else 0)
        result['encoding'] = best_encoding
        result['bits'] = best_bits
    
    elif encoding == 'manchester':
        result['bits'] = decode_manchester(binary_signal)
    elif encoding == 'ook':
        result['bits'] = decode_ook(binary_signal)
    elif encoding == 'pwm':
        result['bits'] = decode_pwm(binary_signal)
    
    if result['bits']:
        # Look for preamble
        preamble_idx = find_preamble(result['bits'])
        if preamble_idx >= 0:
            result['preamble_found'] = True
            result['preamble_index'] = preamble_idx
            
            # Extract data after preamble
            data_bits = extract_data_bits(result['bits'], preamble_idx + 8)
            result['data_bits'] = data_bits
            result['hex_data'] = bits_to_hex(data_bits)
        else:
            # No preamble found, use all bits as data
            result['hex_data'] = bits_to_hex(result['bits'])
    
    return result