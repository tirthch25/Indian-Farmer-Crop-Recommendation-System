"""
Generate Training Data & Train Crop Suitability Model

1. Generates labeled training data using the rule-based scoring engine
2. Trains a Random Forest model on the generated data
3. Evaluates and saves the model

Usage:
    python scripts/train_crop_model.py
    python scripts/train_crop_model.py --scenarios 100 --estimators 300
"""

import sys
import os
import argparse
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from pathlib import Path
from src.ml.pipeline import CropTrainingDataGenerator
from src.ml.predictor import CropSuitabilityRF, plot_feature_importance

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Train crop suitability model')
    parser.add_argument('--scenarios', type=int, default=50, help='Weather scenarios per combination')
    parser.add_argument('--estimators', type=int, default=200, help='Number of trees')
    parser.add_argument('--max-depth', type=int, default=15, help='Max tree depth')
    parser.add_argument('--regenerate', action='store_true', help='Force regenerate training data')
    
    args = parser.parse_args()
    
    training_data_path = Path("data/ml/training/crop_suitability/crop_suitability_data.csv")
    
    # --- Step 1: Generate or load training data ---
    if not training_data_path.exists() or args.regenerate:
        print(f"\n{'='*60}")
        print(f"  Generating Training Data")
        print(f"  Scenarios per combination: {args.scenarios}")
        print(f"{'='*60}")
        
        generator = CropTrainingDataGenerator()
        data = generator.generate_training_data(
            num_weather_scenarios=args.scenarios,
            random_seed=42
        )
        
        # Save training data
        training_data_path.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(training_data_path, index=False)
        print(f"  ✓ Saved {len(data)} records to {training_data_path}")
    else:
        print(f"\n  Loading existing training data from {training_data_path}")
        data = pd.read_csv(training_data_path)
        print(f"  ✓ Loaded {len(data)} records")
    
    # --- Step 2: Train Random Forest model ---
    print(f"\n{'='*60}")
    print(f"  Training Random Forest Model")
    print(f"  Estimators: {args.estimators}, Max Depth: {args.max_depth}")
    print(f"{'='*60}")
    
    model = CropSuitabilityRF()
    results = model.train(
        data,
        target_col='suitability_score',
        n_estimators=args.estimators,
        max_depth=args.max_depth
    )
    
    # --- Step 3: Feature importance ---
    print(f"\n{'='*60}")
    print(f"  Feature Importance Analysis")
    print(f"{'='*60}")
    
    top_features = model.get_feature_importance(top_n=15)
    for feat in top_features:
        bar = '█' * int(feat['importance'] * 100)
        print(f"  {feat['feature']:<25} {feat['importance']:.4f} {bar}")
    
    # Plot feature importance
    if model.feature_names and model.feature_importances is not None:
        plot_feature_importance(
            model.feature_names,
            model.feature_importances,
            title="Crop Suitability — Feature Importance",
            save_path="models/crop_suitability/feature_importance.png"
        )
    
    # --- Step 4: Save model ---
    model.save()
    print(f"\n  ✓ Model saved to models/crop_suitability/")
    
    # --- Summary ---
    print(f"\n{'='*60}")
    print(f"  TRAINING COMPLETE")
    print(f"{'='*60}")
    print(f"  Train R²: {results['train_metrics']['r2']:.4f}")
    print(f"  Test R²:  {results['test_metrics']['r2']:.4f}")
    print(f"  Test MAE: {results['test_metrics']['mae']:.4f}")
    print(f"  Test RMSE:{results['test_metrics']['rmse']:.4f}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
