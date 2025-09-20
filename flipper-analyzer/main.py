"""
Main entry point for Flipper Zero .sub file analyzer
Provides command-line interface and example usage
"""

import sys
import argparse
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzers.reader import parse_sub_file, get_signal_stats
from analyzers.classifier import classify_signal, get_classification_summary, compare_signals
from analyzers.protocol import identify_protocol, extract_protocol_fields
from analyzers.decoder import decode_signal
from utils.plotter import plot_signal, plot_classification_results, plot_spectrum_analysis, save_analysis_report


def analyze_single_file(file_path: str, show_plots: bool = True, save_output: bool = False):
    """
    Analyze a single .sub file
    
    Args:
        file_path: Path to the .sub file
        show_plots: Whether to display plots
        save_output: Whether to save analysis output
    """
    print(f"Analyzing file: {file_path}")
    print("=" * 50)
    
    try:
        # Parse the file
        signal = parse_sub_file(file_path)
        print("✓ File parsed successfully")
        
        # Get basic signal statistics
        stats = get_signal_stats(signal)
        print("\nSignal Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Classify the signal
        classification = classify_signal(signal)
        print(f"\n{get_classification_summary(classification)}")
        
        # Identify protocol
        protocol_info = identify_protocol(signal)
        print(f"\nProtocol Analysis:")
        print(f"  Best Match: {protocol_info['identified_protocol']}")
        print(f"  Confidence: {protocol_info['confidence']:.2%}")
        
        if protocol_info['matches']:
            print("  Other Candidates:")
            for match in protocol_info['matches'][:3]:
                print(f"    • {match['protocol']}: {match['confidence']:.2%}")
        
        # Extract protocol fields if available
        if protocol_info['identified_protocol'] != 'Unknown':
            fields = extract_protocol_fields(signal, protocol_info['identified_protocol'])
            if fields['fields']:
                print(f"\nProtocol Fields ({fields['protocol']}):")
                for field, value in fields['fields'].items():
                    print(f"  {field}: {value}")
                print(f"  Interpretation: {fields['interpretation']}")
        
        # Decode signal details
        decoded = decode_signal(signal, 'auto')
        if decoded.get('hex_data'):
            print(f"\nDecoded Data:")
            print(f"  Hex: {decoded['hex_data']}")
            print(f"  Encoding: {decoded['encoding']}")
            print(f"  Bits: {len(decoded.get('bits', []))}")
        
        # Generate plots if requested
        if show_plots:
            print("\nGenerating visualizations...")
            plot_signal(signal, f"Analysis: {os.path.basename(file_path)}")
            plot_classification_results(classification, f"Classification: {os.path.basename(file_path)}")
        
        # Save output if requested
        if save_output:
            output_dir = f"analysis_{Path(file_path).stem}"
            print(f"\nSaving analysis to {output_dir}/")
            save_analysis_report(signal, classification, output_dir)
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
    except Exception as e:
        print(f"Error analyzing file: {e}")


def compare_files(file1_path: str, file2_path: str, show_plots: bool = True):
    """
    Compare two .sub files
    
    Args:
        file1_path: Path to first .sub file
        file2_path: Path to second .sub file
        show_plots: Whether to display plots
    """
    print(f"Comparing files:")
    print(f"  File 1: {file1_path}")
    print(f"  File 2: {file2_path}")
    print("=" * 50)
    
    try:
        # Parse both files
        signal1 = parse_sub_file(file1_path)
        signal2 = parse_sub_file(file2_path)
        print("✓ Both files parsed successfully")
        
        # Compare signals
        comparison = compare_signals(signal1, signal2)
        
        print(f"\nComparison Results:")
        print(f"  Same Device Probability: {comparison['same_device_probability']:.2%}")
        
        if comparison['similarities']:
            print("\n  Similarities:")
            for similarity in comparison['similarities']:
                print(f"    • {similarity}")
        
        if comparison['differences']:
            print("\n  Differences:")
            for difference in comparison['differences']:
                print(f"    • {difference}")
        
        # Analyze each signal
        class1 = classify_signal(signal1)
        class2 = classify_signal(signal2)
        
        print(f"\n  Signal 1: {class1.signal_type} ({class1.confidence:.2%} confidence)")
        print(f"  Signal 2: {class2.signal_type} ({class2.confidence:.2%} confidence)")
        
        # Generate comparison plots if requested
        if show_plots:
            print("\nGenerating comparison plots...")
            from utils.plotter import plot_comparison
            plot_comparison(signal1, signal2, 
                          f"Comparison: {os.path.basename(file1_path)} vs {os.path.basename(file2_path)}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error comparing files: {e}")


def run_example():
    """Run example analysis with sample data"""
    print("Running Example Analysis")
    print("=" * 30)
    
    sample_path = "examples/sample1.sub"
    
    if not os.path.exists(sample_path):
        print(f"Error: Sample file '{sample_path}' not found")
        print("Please make sure the sample file exists in the examples/ directory")
        return
    
    analyze_single_file(sample_path, show_plots=True, save_output=False)


def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(
        description="Flipper Zero .sub file analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py examples/sample1.sub                    # Analyze single file
  python main.py examples/sample1.sub --save             # Save analysis output
  python main.py --compare file1.sub file2.sub           # Compare two files
  python main.py --example                               # Run example analysis
        """
    )
    
    parser.add_argument('file', nargs='?', help='Path to .sub file to analyze')
    parser.add_argument('--compare', nargs=2, metavar=('FILE1', 'FILE2'),
                       help='Compare two .sub files')
    parser.add_argument('--example', action='store_true',
                       help='Run example analysis with sample data')
    parser.add_argument('--no-plots', action='store_true',
                       help='Disable plot generation')
    parser.add_argument('--save', action='store_true',
                       help='Save analysis output to directory')
    
    args = parser.parse_args()
    
    # Check if matplotlib is available for plotting
    show_plots = not args.no_plots
    if show_plots:
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("Warning: matplotlib not available, disabling plots")
            show_plots = False
    
    if args.example:
        run_example()
    elif args.compare:
        compare_files(args.compare[0], args.compare[1], show_plots)
    elif args.file:
        analyze_single_file(args.file, show_plots, args.save)
    else:
        # No arguments provided, show help and run example
        parser.print_help()
        print("\n" + "="*50)
        print("No file specified. Running example analysis...")
        print("="*50)
        run_example()


if __name__ == "__main__":
    main()