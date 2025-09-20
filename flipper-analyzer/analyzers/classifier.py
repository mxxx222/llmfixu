"""
Signal classifier module for Flipper Zero .sub files
Classifies signals as rolling code or fixed code based on various characteristics
"""

from typing import Dict, List, Tuple, Optional
from .reader import SubFileData
from .decoder import decode_signal
from .protocol import identify_protocol


class SignalClassification:
    """Container for signal classification results"""
    
    def __init__(self):
        self.signal_type: str = "Unknown"  # "Rolling", "Fixed", "Unknown"
        self.confidence: float = 0.0
        self.characteristics: Dict[str, any] = {}
        self.reasoning: List[str] = []
        self.protocol_info: Dict[str, any] = {}


def classify_signal(data: SubFileData) -> SignalClassification:
    """
    Main function to classify signal as rolling or fixed code
    
    Args:
        data: Parsed sub file data
        
    Returns:
        SignalClassification object with results
    """
    classification = SignalClassification()
    
    if not data.raw_pulses:
        classification.reasoning.append("No signal data available")
        return classification
    
    # Get protocol identification
    protocol_info = identify_protocol(data)
    classification.protocol_info = protocol_info
    
    # Decode signal
    decoded = decode_signal(data, 'auto')
    
    # Analyze various characteristics
    characteristics = _analyze_classification_characteristics(data, decoded, protocol_info)
    classification.characteristics = characteristics
    
    # Apply classification rules
    classification = _apply_classification_rules(classification, characteristics)
    
    return classification


def _analyze_classification_characteristics(data: SubFileData, decoded: Dict, protocol_info: Dict) -> Dict[str, any]:
    """Analyze characteristics relevant for rolling vs fixed classification"""
    
    characteristics = {
        # Basic signal properties
        'frequency': data.frequency,
        'total_pulses': len(data.raw_pulses),
        'decoded_bits': len(decoded.get('bits', [])),
        'encoding': decoded.get('encoding', 'unknown'),
        'has_preamble': decoded.get('preamble_found', False),
        
        # Protocol information
        'identified_protocol': protocol_info.get('identified_protocol', 'Unknown'),
        'protocol_confidence': protocol_info.get('confidence', 0.0),
        
        # Classification-specific features
        'bit_length_category': '',
        'complexity_score': 0.0,
        'entropy_score': 0.0,
        'pattern_repetition': 0.0,
        'encoding_complexity': '',
        'frequency_category': '',
    }
    
    # Categorize bit length
    bit_count = len(decoded.get('bits', []))
    if bit_count < 20:
        characteristics['bit_length_category'] = 'short'
    elif bit_count < 40:
        characteristics['bit_length_category'] = 'medium'
    elif bit_count < 70:
        characteristics['bit_length_category'] = 'long'
    else:
        characteristics['bit_length_category'] = 'very_long'
    
    # Calculate complexity score
    characteristics['complexity_score'] = _calculate_complexity_score(decoded.get('bits', []))
    
    # Calculate entropy score
    characteristics['entropy_score'] = _calculate_entropy_score(decoded.get('bits', []))
    
    # Analyze pattern repetition
    characteristics['pattern_repetition'] = _analyze_pattern_repetition(decoded.get('bits', []))
    
    # Categorize encoding complexity
    encoding = decoded.get('encoding', 'unknown')
    if encoding in ['ook']:
        characteristics['encoding_complexity'] = 'simple'
    elif encoding in ['pwm', 'manchester']:
        characteristics['encoding_complexity'] = 'complex'
    else:
        characteristics['encoding_complexity'] = 'unknown'
    
    # Categorize frequency
    freq = data.frequency
    if 300000000 <= freq <= 350000000:
        characteristics['frequency_category'] = 'low_uhf'
    elif 350000000 <= freq <= 400000000:
        characteristics['frequency_category'] = 'mid_uhf'
    elif 400000000 <= freq <= 450000000:
        characteristics['frequency_category'] = 'high_uhf'
    else:
        characteristics['frequency_category'] = 'other'
    
    return characteristics


def _calculate_complexity_score(bits: List[int]) -> float:
    """Calculate complexity score based on bit patterns"""
    if not bits:
        return 0.0
    
    # Count transitions (changes between 0 and 1)
    transitions = sum(1 for i in range(1, len(bits)) if bits[i] != bits[i-1])
    
    # Normalize by bit length
    complexity = transitions / len(bits) if len(bits) > 0 else 0
    
    return complexity


def _calculate_entropy_score(bits: List[int]) -> float:
    """Calculate entropy score of the bit sequence"""
    if not bits:
        return 0.0
    
    # Count frequency of 0s and 1s
    ones = sum(bits)
    zeros = len(bits) - ones
    total = len(bits)
    
    if zeros == 0 or ones == 0:
        return 0.0  # No entropy if all bits are the same
    
    # Calculate Shannon entropy
    p_zero = zeros / total
    p_one = ones / total
    
    import math
    entropy = -(p_zero * math.log2(p_zero) + p_one * math.log2(p_one))
    
    return entropy


def _analyze_pattern_repetition(bits: List[int]) -> float:
    """Analyze how much the bit pattern repeats"""
    if len(bits) < 8:
        return 0.0
    
    # Look for repeated patterns of different lengths
    max_repetition = 0.0
    
    for pattern_length in range(2, min(16, len(bits) // 2)):
        pattern = bits[:pattern_length]
        repetitions = 0
        
        for i in range(pattern_length, len(bits) - pattern_length + 1, pattern_length):
            if bits[i:i + pattern_length] == pattern:
                repetitions += 1
        
        repetition_ratio = repetitions / (len(bits) // pattern_length)
        max_repetition = max(max_repetition, repetition_ratio)
    
    return max_repetition


def _apply_classification_rules(classification: SignalClassification, characteristics: Dict) -> SignalClassification:
    """Apply rules to classify as rolling or fixed code"""
    
    rolling_score = 0.0
    fixed_score = 0.0
    reasoning = []
    
    # Rule 1: Protocol-based classification
    protocol = characteristics.get('identified_protocol', '').lower()
    protocol_confidence = characteristics.get('protocol_confidence', 0.0)
    
    if protocol_confidence > 0.5:
        if protocol in ['keeloq', 'hcs301', 'hcs200', 'faac slh', 'chamberlain']:
            rolling_score += 0.4
            reasoning.append(f"Protocol {protocol} is typically rolling code")
        elif protocol in ['princeton', 'fixed code', 'came', 'nice flo', 'linear']:
            fixed_score += 0.4
            reasoning.append(f"Protocol {protocol} is typically fixed code")
    
    # Rule 2: Bit length analysis
    bit_length_cat = characteristics.get('bit_length_category', '')
    if bit_length_cat == 'very_long':
        rolling_score += 0.3
        reasoning.append("Very long bit length suggests rolling code")
    elif bit_length_cat == 'long':
        rolling_score += 0.2
        reasoning.append("Long bit length suggests rolling code")
    elif bit_length_cat in ['short', 'medium']:
        fixed_score += 0.2
        reasoning.append("Shorter bit length suggests fixed code")
    
    # Rule 3: Encoding complexity
    encoding_complexity = characteristics.get('encoding_complexity', '')
    if encoding_complexity == 'complex':
        rolling_score += 0.15
        reasoning.append("Complex encoding (PWM/Manchester) often used in rolling codes")
    elif encoding_complexity == 'simple':
        fixed_score += 0.1
        reasoning.append("Simple encoding (OOK) often used in fixed codes")
    
    # Rule 4: Signal complexity
    complexity_score = characteristics.get('complexity_score', 0.0)
    if complexity_score > 0.4:
        rolling_score += 0.1
        reasoning.append("High signal complexity suggests rolling code")
    elif complexity_score < 0.2:
        fixed_score += 0.1
        reasoning.append("Low signal complexity suggests fixed code")
    
    # Rule 5: Entropy analysis
    entropy_score = characteristics.get('entropy_score', 0.0)
    if entropy_score > 0.8:
        rolling_score += 0.1
        reasoning.append("High entropy suggests rolling code")
    elif entropy_score < 0.5:
        fixed_score += 0.05
        reasoning.append("Low entropy suggests fixed code")
    
    # Rule 6: Pattern repetition
    pattern_repetition = characteristics.get('pattern_repetition', 0.0)
    if pattern_repetition > 0.7:
        fixed_score += 0.15
        reasoning.append("High pattern repetition suggests fixed code")
    elif pattern_repetition < 0.3:
        rolling_score += 0.1
        reasoning.append("Low pattern repetition suggests rolling code")
    
    # Rule 7: Frequency band analysis
    frequency_category = characteristics.get('frequency_category', '')
    if frequency_category in ['mid_uhf', 'high_uhf']:
        # 433 MHz band often used for rolling codes
        rolling_score += 0.05
    
    # Determine final classification
    total_score = rolling_score + fixed_score
    
    if total_score > 0:
        rolling_confidence = rolling_score / total_score
        fixed_confidence = fixed_score / total_score
        
        if rolling_confidence > 0.6:
            classification.signal_type = "Rolling"
            classification.confidence = rolling_confidence
        elif fixed_confidence > 0.6:
            classification.signal_type = "Fixed"
            classification.confidence = fixed_confidence
        else:
            classification.signal_type = "Uncertain"
            classification.confidence = max(rolling_confidence, fixed_confidence)
            reasoning.append("Classification uncertain due to mixed indicators")
    else:
        classification.signal_type = "Unknown"
        classification.confidence = 0.0
        reasoning.append("Insufficient data for classification")
    
    classification.reasoning = reasoning
    return classification


def get_classification_summary(classification: SignalClassification) -> str:
    """
    Get a human-readable summary of the classification
    
    Args:
        classification: SignalClassification object
        
    Returns:
        Formatted summary string
    """
    summary_lines = [
        f"Signal Type: {classification.signal_type}",
        f"Confidence: {classification.confidence:.2%}",
        "",
        "Analysis:"
    ]
    
    for reason in classification.reasoning:
        summary_lines.append(f"  • {reason}")
    
    if classification.protocol_info.get('identified_protocol') != 'Unknown':
        summary_lines.extend([
            "",
            f"Identified Protocol: {classification.protocol_info['identified_protocol']}",
            f"Protocol Confidence: {classification.protocol_info.get('confidence', 0):.2%}"
        ])
    
    # Add key characteristics
    chars = classification.characteristics
    if chars:
        summary_lines.extend([
            "",
            "Key Characteristics:",
            f"  • Bit Length: {chars.get('decoded_bits', 0)} bits ({chars.get('bit_length_category', 'unknown')})",
            f"  • Encoding: {chars.get('encoding', 'unknown')} ({chars.get('encoding_complexity', 'unknown')} complexity)",
            f"  • Signal Complexity: {chars.get('complexity_score', 0):.3f}",
            f"  • Entropy Score: {chars.get('entropy_score', 0):.3f}",
            f"  • Pattern Repetition: {chars.get('pattern_repetition', 0):.3f}"
        ])
    
    return "\n".join(summary_lines)


def compare_signals(data1: SubFileData, data2: SubFileData) -> Dict[str, any]:
    """
    Compare two signals to see if they might be from the same transmitter
    
    Args:
        data1: First signal data
        data2: Second signal data
        
    Returns:
        Dictionary with comparison results
    """
    result = {
        'same_device_probability': 0.0,
        'differences': [],
        'similarities': [],
        'analysis': {}
    }
    
    # Classify both signals
    class1 = classify_signal(data1)
    class2 = classify_signal(data2)
    
    similarity_score = 0.0
    
    # Compare frequencies
    if abs(data1.frequency - data2.frequency) < 1000:  # Within 1 kHz
        similarity_score += 0.3
        result['similarities'].append("Same frequency")
    else:
        result['differences'].append(f"Different frequencies: {data1.frequency} vs {data2.frequency}")
    
    # Compare protocols
    protocol1 = class1.protocol_info.get('identified_protocol', 'Unknown')
    protocol2 = class2.protocol_info.get('identified_protocol', 'Unknown')
    
    if protocol1 == protocol2 and protocol1 != 'Unknown':
        similarity_score += 0.3
        result['similarities'].append(f"Same protocol: {protocol1}")
    elif protocol1 != protocol2:
        result['differences'].append(f"Different protocols: {protocol1} vs {protocol2}")
    
    # Compare signal types
    if class1.signal_type == class2.signal_type:
        similarity_score += 0.2
        result['similarities'].append(f"Same signal type: {class1.signal_type}")
    else:
        result['differences'].append(f"Different signal types: {class1.signal_type} vs {class2.signal_type}")
    
    # Compare bit lengths
    bits1 = class1.characteristics.get('decoded_bits', 0)
    bits2 = class2.characteristics.get('decoded_bits', 0)
    
    if abs(bits1 - bits2) <= 2:  # Allow small differences
        similarity_score += 0.1
        result['similarities'].append("Similar bit lengths")
    else:
        result['differences'].append(f"Different bit lengths: {bits1} vs {bits2}")
    
    # Compare encodings
    enc1 = class1.characteristics.get('encoding', 'unknown')
    enc2 = class2.characteristics.get('encoding', 'unknown')
    
    if enc1 == enc2:
        similarity_score += 0.1
        result['similarities'].append(f"Same encoding: {enc1}")
    else:
        result['differences'].append(f"Different encodings: {enc1} vs {enc2}")
    
    result['same_device_probability'] = similarity_score
    result['analysis'] = {
        'signal1_type': class1.signal_type,
        'signal2_type': class2.signal_type,
        'similarity_score': similarity_score
    }
    
    return result