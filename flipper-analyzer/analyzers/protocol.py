"""
Protocol identification module for Flipper Zero .sub files
Identifies common RF protocols based on signal characteristics
"""

import re
from typing import Dict, List, Optional, Tuple
from .reader import SubFileData
from .decoder import decode_signal


class ProtocolSignature:
    """Container for protocol signature information"""
    
    def __init__(self, name: str, frequency_range: Tuple[int, int], 
                 typical_bit_length: int, encoding: str, 
                 preamble_pattern: List[int] = None, description: str = ""):
        self.name = name
        self.frequency_range = frequency_range
        self.typical_bit_length = typical_bit_length
        self.encoding = encoding
        self.preamble_pattern = preamble_pattern or []
        self.description = description


# Common RF protocol signatures
PROTOCOL_SIGNATURES = [
    ProtocolSignature(
        name="KeeLoq",
        frequency_range=(315000000, 434000000),
        typical_bit_length=66,
        encoding="pwm",
        preamble_pattern=[1, 0, 1, 0, 1, 0, 1, 0],
        description="Rolling code protocol used in car remotes"
    ),
    ProtocolSignature(
        name="Fixed Code",
        frequency_range=(300000000, 450000000),
        typical_bit_length=24,
        encoding="ook",
        preamble_pattern=[1, 0, 1, 0, 1, 0],
        description="Simple fixed code protocol"
    ),
    ProtocolSignature(
        name="HCS301",
        frequency_range=(315000000, 434000000),
        typical_bit_length=66,
        encoding="pwm",
        description="Microchip HCS301 rolling code"
    ),
    ProtocolSignature(
        name="HCS200",
        frequency_range=(315000000, 434000000),
        typical_bit_length=66,
        encoding="pwm",
        description="Microchip HCS200 rolling code"
    ),
    ProtocolSignature(
        name="Princeton",
        frequency_range=(315000000, 434000000),
        typical_bit_length=24,
        encoding="ook",
        description="Princeton PT2262/PT2272 protocol"
    ),
    ProtocolSignature(
        name="CAME",
        frequency_range=(433920000, 433920000),
        typical_bit_length=12,
        encoding="ook",
        description="CAME gate remote protocol"
    ),
    ProtocolSignature(
        name="Nice FLO",
        frequency_range=(433920000, 433920000),
        typical_bit_length=12,
        encoding="ook",
        description="Nice FLO protocol"
    ),
    ProtocolSignature(
        name="Chamberlain",
        frequency_range=(315000000, 390000000),
        typical_bit_length=32,
        encoding="pwm",
        description="Chamberlain garage door opener"
    ),
    ProtocolSignature(
        name="Linear",
        frequency_range=(300000000, 400000000),
        typical_bit_length=20,
        encoding="ook",
        description="Linear garage door opener"
    ),
    ProtocolSignature(
        name="FAAC SLH",
        frequency_range=(433920000, 433920000),
        typical_bit_length=64,
        encoding="pwm",
        description="FAAC SLH rolling code"
    )
]


def identify_protocol(data: SubFileData) -> Dict[str, any]:
    """
    Identify the most likely protocol for the given signal
    
    Args:
        data: Parsed sub file data
        
    Returns:
        Dictionary with protocol identification results
    """
    result = {
        'identified_protocol': 'Unknown',
        'confidence': 0.0,
        'matches': [],
        'signal_characteristics': {},
        'decoded_data': {}
    }
    
    if not data.raw_pulses:
        return result
    
    # First try to decode the signal
    decoded = decode_signal(data, 'auto')
    result['decoded_data'] = decoded
    
    # Analyze signal characteristics
    characteristics = _analyze_signal_characteristics(data, decoded)
    result['signal_characteristics'] = characteristics
    
    # Check against known protocol signatures
    matches = []
    
    for signature in PROTOCOL_SIGNATURES:
        confidence = _calculate_protocol_confidence(data, decoded, characteristics, signature)
        if confidence > 0.1:  # Only include if there's some confidence
            matches.append({
                'protocol': signature.name,
                'confidence': confidence,
                'description': signature.description,
                'reasons': _get_match_reasons(data, decoded, characteristics, signature)
            })
    
    # Sort by confidence
    matches.sort(key=lambda x: x['confidence'], reverse=True)
    result['matches'] = matches
    
    if matches:
        result['identified_protocol'] = matches[0]['protocol']
        result['confidence'] = matches[0]['confidence']
    
    return result


def _analyze_signal_characteristics(data: SubFileData, decoded: Dict) -> Dict[str, any]:
    """Analyze basic signal characteristics"""
    characteristics = {
        'frequency': data.frequency,
        'total_pulses': len(data.raw_pulses),
        'decoded_bits': len(decoded.get('bits', [])),
        'encoding_used': decoded.get('encoding', 'unknown'),
        'has_preamble': decoded.get('preamble_found', False),
        'avg_pulse_duration': 0,
        'pulse_duration_variance': 0,
        'duty_cycle': 0
    }
    
    if data.raw_pulses:
        import numpy as np
        characteristics['avg_pulse_duration'] = np.mean(data.raw_pulses)
        characteristics['pulse_duration_variance'] = np.var(data.raw_pulses)
        
        # Calculate duty cycle (ratio of high to low pulses)
        high_pulses = data.raw_pulses[::2]  # Assuming alternating high/low
        low_pulses = data.raw_pulses[1::2]
        
        if high_pulses and low_pulses:
            total_high = sum(high_pulses)
            total_low = sum(low_pulses)
            characteristics['duty_cycle'] = total_high / (total_high + total_low)
    
    return characteristics


def _calculate_protocol_confidence(data: SubFileData, decoded: Dict, 
                                 characteristics: Dict, signature: ProtocolSignature) -> float:
    """Calculate confidence score for a protocol match"""
    confidence = 0.0
    
    # Frequency match (40% weight)
    freq_min, freq_max = signature.frequency_range
    if freq_min <= data.frequency <= freq_max:
        confidence += 0.4
    elif abs(data.frequency - freq_min) < 50000000:  # Close to range
        confidence += 0.2
    
    # Bit length match (30% weight)
    decoded_bits = len(decoded.get('bits', []))
    if decoded_bits > 0:
        bit_length_diff = abs(decoded_bits - signature.typical_bit_length)
        if bit_length_diff == 0:
            confidence += 0.3
        elif bit_length_diff <= 5:
            confidence += 0.2
        elif bit_length_diff <= 10:
            confidence += 0.1
    
    # Encoding match (20% weight)
    if decoded.get('encoding') == signature.encoding:
        confidence += 0.2
    
    # Preamble pattern match (10% weight)
    if signature.preamble_pattern and decoded.get('preamble_found'):
        confidence += 0.1
    
    return min(confidence, 1.0)  # Cap at 1.0


def _get_match_reasons(data: SubFileData, decoded: Dict, 
                      characteristics: Dict, signature: ProtocolSignature) -> List[str]:
    """Get human-readable reasons for protocol match"""
    reasons = []
    
    # Check frequency
    freq_min, freq_max = signature.frequency_range
    if freq_min <= data.frequency <= freq_max:
        reasons.append(f"Frequency {data.frequency} Hz matches expected range")
    
    # Check bit length
    decoded_bits = len(decoded.get('bits', []))
    if abs(decoded_bits - signature.typical_bit_length) <= 5:
        reasons.append(f"Bit length {decoded_bits} close to expected {signature.typical_bit_length}")
    
    # Check encoding
    if decoded.get('encoding') == signature.encoding:
        reasons.append(f"Encoding type {signature.encoding} matches")
    
    # Check preamble
    if signature.preamble_pattern and decoded.get('preamble_found'):
        reasons.append("Preamble pattern detected")
    
    return reasons


def analyze_rolling_code_pattern(data: SubFileData, protocol: str = None) -> Dict[str, any]:
    """
    Analyze if the signal shows rolling code characteristics
    
    Args:
        data: Parsed sub file data
        protocol: Suspected protocol name
        
    Returns:
        Dictionary with rolling code analysis
    """
    result = {
        'is_rolling_code': False,
        'analysis': {},
        'recommendations': []
    }
    
    decoded = decode_signal(data, 'auto')
    
    if not decoded.get('bits'):
        result['analysis']['error'] = "No decoded bits available"
        return result
    
    bits = decoded['bits']
    
    # Look for rolling code indicators
    analysis = {
        'bit_length': len(bits),
        'has_sync_pattern': decoded.get('preamble_found', False),
        'encoding': decoded.get('encoding', 'unknown')
    }
    
    # Check if bit length suggests rolling code
    if len(bits) >= 64:  # Rolling codes are typically longer
        analysis['length_suggests_rolling'] = True
        result['is_rolling_code'] = True
        result['recommendations'].append("Long bit length suggests rolling code protocol")
    else:
        analysis['length_suggests_rolling'] = False
        result['recommendations'].append("Short bit length suggests fixed code protocol")
    
    # Check encoding type
    if decoded.get('encoding') == 'pwm':
        analysis['encoding_suggests_rolling'] = True
        result['recommendations'].append("PWM encoding commonly used in rolling codes")
    else:
        analysis['encoding_suggests_rolling'] = False
    
    # Protocol-specific analysis
    if protocol:
        if protocol.lower() in ['keeloq', 'hcs301', 'hcs200', 'faac slh']:
            result['is_rolling_code'] = True
            result['recommendations'].append(f"{protocol} is a known rolling code protocol")
        elif protocol.lower() in ['princeton', 'fixed code', 'came', 'nice flo']:
            result['is_rolling_code'] = False
            result['recommendations'].append(f"{protocol} is typically a fixed code protocol")
    
    result['analysis'] = analysis
    return result


def extract_protocol_fields(data: SubFileData, protocol: str) -> Dict[str, any]:
    """
    Extract protocol-specific fields from decoded data
    
    Args:
        data: Parsed sub file data
        protocol: Identified protocol name
        
    Returns:
        Dictionary with extracted protocol fields
    """
    result = {
        'protocol': protocol,
        'fields': {},
        'raw_data': '',
        'interpretation': ''
    }
    
    decoded = decode_signal(data, 'auto')
    
    if not decoded.get('bits'):
        return result
    
    bits = decoded['bits']
    result['raw_data'] = decoded.get('hex_data', '')
    
    # Protocol-specific field extraction
    if protocol.lower() == 'keeloq':
        result['fields'] = _extract_keeloq_fields(bits)
        result['interpretation'] = "KeeLoq rolling code with encrypted counter"
    
    elif protocol.lower() in ['princeton', 'fixed code']:
        result['fields'] = _extract_princeton_fields(bits)
        result['interpretation'] = "Fixed code with device ID and button pattern"
    
    elif protocol.lower() == 'came':
        result['fields'] = _extract_came_fields(bits)
        result['interpretation'] = "CAME protocol with device address"
    
    else:
        # Generic extraction
        result['fields'] = _extract_generic_fields(bits)
        result['interpretation'] = f"Generic {protocol} protocol data"
    
    return result


def _extract_keeloq_fields(bits: List[int]) -> Dict[str, str]:
    """Extract KeeLoq protocol fields"""
    fields = {}
    
    if len(bits) >= 66:
        # KeeLoq format: 32-bit encrypted + 28-bit serial + other fields
        encrypted_part = bits[:32]
        serial_part = bits[32:60]
        
        fields['encrypted_counter'] = ''.join(map(str, encrypted_part))
        fields['serial_number'] = ''.join(map(str, serial_part))
        fields['button_state'] = ''.join(map(str, bits[60:64])) if len(bits) >= 64 else ''
    
    return fields


def _extract_princeton_fields(bits: List[int]) -> Dict[str, str]:
    """Extract Princeton PT2262 protocol fields"""
    fields = {}
    
    if len(bits) >= 20:
        # Princeton format: address + data
        address_bits = bits[:16] if len(bits) >= 16 else bits[:12]
        data_bits = bits[16:] if len(bits) >= 16 else bits[12:]
        
        fields['address'] = ''.join(map(str, address_bits))
        fields['data'] = ''.join(map(str, data_bits))
    
    return fields


def _extract_came_fields(bits: List[int]) -> Dict[str, str]:
    """Extract CAME protocol fields"""
    fields = {}
    
    if len(bits) >= 12:
        fields['device_code'] = ''.join(map(str, bits))
    
    return fields


def _extract_generic_fields(bits: List[int]) -> Dict[str, str]:
    """Extract generic protocol fields"""
    fields = {}
    
    if bits:
        fields['raw_bits'] = ''.join(map(str, bits))
        fields['bit_count'] = str(len(bits))
    
    return fields