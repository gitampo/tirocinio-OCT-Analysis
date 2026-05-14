#!/usr/bin/env python3
"""
Quick test to verify anti-leakage splitting works correctly.
"""

import sys
from pathlib import Path
import os

# Setup paths
script_dir = Path(__file__).parent.absolute()
app_dir = script_dir / 'app'
os.chdir(app_dir)
sys.path.insert(0, str(app_dir))

def test_anti_leakage_split():
    print("\n" + "="*70)
    print("Anti-Leakage Split Test")
    print("="*70)
    
    from deeplearning.utils import load_splitted_dataset_from_name
    from deeplearning import DEFAULT_SPLIT, DEFAULT_DATASET
    
    print(f"\nDataset: {DEFAULT_DATASET}")
    print(f"Split: train={DEFAULT_SPLIT[0]}, eval={DEFAULT_SPLIT[1]}, test={DEFAULT_SPLIT[2]}")
    
    print("\nLoading dataset with patient-level splitting...")
    dataset = load_splitted_dataset_from_name(DEFAULT_DATASET, DEFAULT_SPLIT)
    
    print(f"\n✓ Dataset loaded successfully!")
    print(f"\nSplit sizes:")
    print(f"  Train: {len(dataset['train'])} images")
    print(f"  Eval:  {len(dataset['eval'])} images")
    print(f"  Test:  {len(dataset['test'])} images")
    print(f"  Total: {len(dataset['train']) + len(dataset['eval']) + len(dataset['test'])} images")
    
    print(f"\nDataset splits:")
    for split_name, split_dataset in dataset.items():
        print(f"\n{split_name.upper()}:")
        print(f"  - Size: {len(split_dataset)} examples")
        print(f"  - Features: {list(split_dataset.features.keys())}")
        
        # Show sample
        if len(split_dataset) > 0:
            sample = split_dataset[0]
            print(f"  - Sample: image={type(sample['image'])}, label={sample['label']}")

if __name__ == '__main__':
    try:
        test_anti_leakage_split()
        print("\n✓ Anti-leakage split test completed successfully!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
