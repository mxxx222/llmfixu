"""
Plotting utilities for Flipper Zero .sub file analysis
Provides matplotlib-based visualizations for signals and analysis results
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Tuple, Optional
import sys
import os

# Add the parent directory to the path to import analyzers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzers.reader import SubFileData, extract_raw_signal
from analyzers.decoder import decode_signal, apply_threshold
from analyzers.classifier import SignalClassification


def plot_signal(data: SubFileData, title: str = "Signal Analysis", save_path: str = None):
    """
    Create a comprehensive plot of the signal data
    
    Args:
        data: Parsed sub file data
        title: Plot title
        save_path: Optional path to save the plot
    """
    if not data.raw_pulses:
        print("No signal data to plot")
        return
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    # Plot 1: Raw pulse durations
    _plot_raw_pulses(axes[0], data)
    
    # Plot 2: Time domain signal
    _plot_time_domain(axes[1], data)
    
    # Plot 3: Binary signal after thresholding
    _plot_binary_signal(axes[2], data)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.show()


def _plot_raw_pulses(ax, data: SubFileData):
    """Plot raw pulse durations as bar chart"""
    pulse_indices = range(len(data.raw_pulses))
    colors = ['red' if i % 2 == 0 else 'blue' for i in pulse_indices]
    
    ax.bar(pulse_indices, data.raw_pulses, color=colors, alpha=0.7)
    ax.set_title('Raw Pulse Durations')
    ax.set_xlabel('Pulse Index')
    ax.set_ylabel('Duration (μs)')
    ax.grid(True, alpha=0.3)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='red', alpha=0.7, label='High Pulses'),
                      Patch(facecolor='blue', alpha=0.7, label='Low Pulses')]
    ax.legend(handles=legend_elements, loc='upper right')


def _plot_time_domain(ax, data: SubFileData):
    """Plot signal in time domain"""
    signal_pairs = extract_raw_signal(data)
    
    if not signal_pairs:
        ax.text(0.5, 0.5, 'No signal data', ha='center', va='center', transform=ax.transAxes)
        return
    
    # Convert to time series
    time_points = []
    signal_levels = []
    current_time = 0
    
    for duration, level in signal_pairs:
        time_points.extend([current_time, current_time + duration])
        signal_levels.extend([level, level])
        current_time += duration
    
    ax.plot(time_points, signal_levels, 'b-', linewidth=1.5)
    ax.set_title('Time Domain Signal')
    ax.set_xlabel('Time (μs)')
    ax.set_ylabel('Signal Level')
    ax.set_ylim(-0.1, 1.1)
    ax.grid(True, alpha=0.3)
    
    # Add frequency info
    freq_mhz = data.frequency / 1000000
    ax.text(0.02, 0.98, f'Frequency: {freq_mhz:.2f} MHz', 
            transform=ax.transAxes, va='top', 
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))


def _plot_binary_signal(ax, data: SubFileData):
    """Plot binary signal after thresholding"""
    decoded = decode_signal(data, 'auto')
    binary_signal = decoded.get('binary_signal', [])
    
    if not binary_signal:
        ax.text(0.5, 0.5, 'No binary data', ha='center', va='center', transform=ax.transAxes)
        return
    
    # Create binary time series
    time_points = []
    levels = []
    current_time = 0
    
    for duration, level in binary_signal:
        time_points.extend([current_time, current_time + duration])
        levels.extend([level, level])
        current_time += duration
    
    ax.plot(time_points, levels, 'g-', linewidth=2)
    ax.set_title(f'Binary Signal (Encoding: {decoded.get("encoding", "unknown")})')
    ax.set_xlabel('Time (μs)')
    ax.set_ylabel('Binary Level')
    ax.set_ylim(-0.1, 1.1)
    ax.grid(True, alpha=0.3)
    
    # Add bit count info
    bit_count = len(decoded.get('bits', []))
    ax.text(0.02, 0.98, f'Decoded Bits: {bit_count}', 
            transform=ax.transAxes, va='top',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))


def plot_spectrum_analysis(data: SubFileData, title: str = "Spectrum Analysis", save_path: str = None):
    """
    Plot frequency spectrum analysis of the signal
    
    Args:
        data: Parsed sub file data
        title: Plot title
        save_path: Optional path to save the plot
    """
    if not data.raw_pulses:
        print("No signal data for spectrum analysis")
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    # Create time series for FFT
    signal_pairs = extract_raw_signal(data)
    time_points = []
    signal_levels = []
    current_time = 0
    
    for duration, level in signal_pairs:
        # Sample at higher rate for better FFT
        samples = max(1, duration // 10)
        for _ in range(samples):
            time_points.append(current_time)
            signal_levels.append(level)
            current_time += 10  # 10 μs sampling
    
    if len(signal_levels) < 2:
        ax1.text(0.5, 0.5, 'Insufficient data for spectrum analysis', 
                ha='center', va='center', transform=ax1.transAxes)
        return
    
    # Convert to numpy arrays
    time_array = np.array(time_points)
    signal_array = np.array(signal_levels)
    
    # Plot time domain
    ax1.plot(time_array, signal_array, 'b-', linewidth=1)
    ax1.set_title('Time Domain Signal')
    ax1.set_xlabel('Time (μs)')
    ax1.set_ylabel('Amplitude')
    ax1.grid(True, alpha=0.3)
    
    # Compute and plot FFT
    sampling_rate = 100000  # 100 kHz (10 μs sampling)
    fft_values = np.fft.fft(signal_array)
    frequencies = np.fft.fftfreq(len(fft_values), 1/sampling_rate)
    
    # Only plot positive frequencies
    positive_freq_mask = frequencies > 0
    ax2.plot(frequencies[positive_freq_mask], 
             np.abs(fft_values[positive_freq_mask]), 'r-', linewidth=1)
    ax2.set_title('Frequency Spectrum')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Magnitude')
    ax2.set_xlim(0, sampling_rate/2)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Spectrum plot saved to {save_path}")
    else:
        plt.show()


def plot_classification_results(classification: SignalClassification, title: str = "Classification Results", save_path: str = None):
    """
    Plot classification results and characteristics
    
    Args:
        classification: SignalClassification object
        save_path: Optional path to save the plot
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    # Plot 1: Classification confidence
    _plot_classification_confidence(ax1, classification)
    
    # Plot 2: Signal characteristics radar chart
    _plot_characteristics_radar(ax2, classification)
    
    # Plot 3: Protocol matches
    _plot_protocol_matches(ax3, classification)
    
    # Plot 4: Feature importance
    _plot_feature_analysis(ax4, classification)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Classification plot saved to {save_path}")
    else:
        plt.show()


def _plot_classification_confidence(ax, classification: SignalClassification):
    """Plot classification confidence as pie chart"""
    if classification.signal_type == "Unknown":
        ax.text(0.5, 0.5, 'Classification:\nUnknown', 
               ha='center', va='center', transform=ax.transAxes, 
               fontsize=14, fontweight='bold')
        return
    
    confidence = classification.confidence
    uncertainty = 1 - confidence
    
    labels = [classification.signal_type, 'Uncertainty']
    sizes = [confidence, uncertainty]
    colors = ['lightgreen' if classification.signal_type == 'Fixed' else 'lightcoral', 'lightgray']
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.set_title(f'Classification: {classification.signal_type}\nConfidence: {confidence:.1%}')


def _plot_characteristics_radar(ax, classification: SignalClassification):
    """Plot signal characteristics as radar chart"""
    characteristics = classification.characteristics
    
    if not characteristics:
        ax.text(0.5, 0.5, 'No characteristics\navailable', 
               ha='center', va='center', transform=ax.transAxes)
        return
    
    # Select key characteristics for radar plot
    features = ['complexity_score', 'entropy_score', 'pattern_repetition']
    values = [characteristics.get(feature, 0) for feature in features]
    labels = ['Complexity', 'Entropy', 'Repetition']
    
    # Normalize values to 0-1 range
    values = [min(1.0, max(0.0, v)) for v in values]
    
    # Create radar plot
    angles = np.linspace(0, 2 * np.pi, len(features), endpoint=False).tolist()
    values += values[:1]  # Complete the circle
    angles += angles[:1]
    
    ax.plot(angles, values, 'o-', linewidth=2, color='blue', alpha=0.7)
    ax.fill(angles, values, alpha=0.25, color='blue')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1)
    ax.set_title('Signal Characteristics')
    ax.grid(True, alpha=0.3)


def _plot_protocol_matches(ax, classification: SignalClassification):
    """Plot protocol identification matches"""
    protocol_info = classification.protocol_info
    matches = protocol_info.get('matches', [])
    
    if not matches:
        ax.text(0.5, 0.5, 'No protocol matches\nfound', 
               ha='center', va='center', transform=ax.transAxes)
        return
    
    # Plot top 5 matches
    top_matches = matches[:5]
    protocols = [match['protocol'] for match in top_matches]
    confidences = [match['confidence'] for match in top_matches]
    
    bars = ax.barh(protocols, confidences, color='skyblue', alpha=0.7)
    ax.set_xlabel('Confidence')
    ax.set_title('Protocol Matches')
    ax.set_xlim(0, 1)
    
    # Add confidence values on bars
    for i, (bar, conf) in enumerate(zip(bars, confidences)):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
               f'{conf:.2f}', va='center', fontsize=10)


def _plot_feature_analysis(ax, classification: SignalClassification):
    """Plot feature importance analysis"""
    characteristics = classification.characteristics
    
    if not characteristics:
        ax.text(0.5, 0.5, 'No feature data\navailable', 
               ha='center', va='center', transform=ax.transAxes)
        return
    
    # Extract key features
    features = {
        'Bit Length': _normalize_bit_length(characteristics.get('decoded_bits', 0)),
        'Complexity': characteristics.get('complexity_score', 0),
        'Entropy': characteristics.get('entropy_score', 0),
        'Repetition': 1 - characteristics.get('pattern_repetition', 0),  # Invert for display
    }
    
    feature_names = list(features.keys())
    feature_values = list(features.values())
    
    bars = ax.bar(feature_names, feature_values, color=['coral', 'lightblue', 'lightgreen', 'gold'], alpha=0.7)
    ax.set_ylabel('Normalized Score')
    ax.set_title('Feature Analysis')
    ax.set_ylim(0, 1)
    
    # Add value labels on bars
    for bar, value in zip(bars, feature_values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
               f'{value:.2f}', ha='center', va='bottom', fontsize=10)


def _normalize_bit_length(bit_length: int) -> float:
    """Normalize bit length to 0-1 scale for plotting"""
    if bit_length <= 20:
        return 0.2
    elif bit_length <= 40:
        return 0.5
    elif bit_length <= 70:
        return 0.8
    else:
        return 1.0


def plot_comparison(data1: SubFileData, data2: SubFileData, 
                   title: str = "Signal Comparison", save_path: str = None):
    """
    Plot comparison between two signals
    
    Args:
        data1: First signal data
        data2: Second signal data
        title: Plot title
        save_path: Optional path to save the plot
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    # Plot raw pulses for both signals
    _plot_comparison_pulses(axes[0, 0], data1, "Signal 1 - Raw Pulses")
    _plot_comparison_pulses(axes[0, 1], data2, "Signal 2 - Raw Pulses")
    
    # Plot time domain for both signals
    _plot_comparison_time_domain(axes[1, 0], data1, "Signal 1 - Time Domain")
    _plot_comparison_time_domain(axes[1, 1], data2, "Signal 2 - Time Domain")
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Comparison plot saved to {save_path}")
    else:
        plt.show()


def _plot_comparison_pulses(ax, data: SubFileData, title: str):
    """Plot pulse data for comparison"""
    if not data.raw_pulses:
        ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
        return
    
    pulse_indices = range(len(data.raw_pulses))
    colors = ['red' if i % 2 == 0 else 'blue' for i in pulse_indices]
    
    ax.bar(pulse_indices, data.raw_pulses, color=colors, alpha=0.7)
    ax.set_title(title)
    ax.set_xlabel('Pulse Index')
    ax.set_ylabel('Duration (μs)')
    ax.grid(True, alpha=0.3)


def _plot_comparison_time_domain(ax, data: SubFileData, title: str):
    """Plot time domain signal for comparison"""
    signal_pairs = extract_raw_signal(data)
    
    if not signal_pairs:
        ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
        return
    
    time_points = []
    signal_levels = []
    current_time = 0
    
    for duration, level in signal_pairs:
        time_points.extend([current_time, current_time + duration])
        signal_levels.extend([level, level])
        current_time += duration
    
    ax.plot(time_points, signal_levels, 'b-', linewidth=1.5)
    ax.set_title(title)
    ax.set_xlabel('Time (μs)')
    ax.set_ylabel('Signal Level')
    ax.set_ylim(-0.1, 1.1)
    ax.grid(True, alpha=0.3)
    
    # Add info
    freq_mhz = data.frequency / 1000000
    ax.text(0.02, 0.98, f'{freq_mhz:.2f} MHz', 
            transform=ax.transAxes, va='top', 
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))


def save_analysis_report(data: SubFileData, classification: SignalClassification, 
                        output_dir: str = "analysis_output"):
    """
    Save a complete analysis report with all plots
    
    Args:
        data: Parsed sub file data
        classification: Signal classification results
        output_dir: Output directory for files
    """
    import os
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate all plots
    plot_signal(data, "Complete Signal Analysis", 
               os.path.join(output_dir, "signal_analysis.png"))
    
    plot_spectrum_analysis(data, "Spectrum Analysis", 
                          os.path.join(output_dir, "spectrum_analysis.png"))
    
    plot_classification_results(classification, "Classification Results", 
                               os.path.join(output_dir, "classification_results.png"))
    
    # Save text report
    report_path = os.path.join(output_dir, "analysis_report.txt")
    with open(report_path, 'w') as f:
        f.write("Flipper Zero .sub File Analysis Report\n")
        f.write("=" * 40 + "\n\n")
        
        f.write("Signal Information:\n")
        f.write(f"  Frequency: {data.frequency} Hz\n")
        f.write(f"  Protocol: {data.protocol}\n")
        f.write(f"  Total Pulses: {len(data.raw_pulses)}\n\n")
        
        f.write("Classification Results:\n")
        f.write(f"  Signal Type: {classification.signal_type}\n")
        f.write(f"  Confidence: {classification.confidence:.2%}\n\n")
        
        f.write("Analysis Reasoning:\n")
        for reason in classification.reasoning:
            f.write(f"  • {reason}\n")
    
    print(f"Analysis report saved to {output_dir}/")