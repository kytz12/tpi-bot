import os
import sys
import pandas as pd
import joblib

def main():
    labels_csv = "data/grid_labels.csv"
    model_path = "models/nadocast_v0_logreg.joblib"

    if not os.path.exists(labels_csv):
        print("Missing data/grid_labels.csv. Run 04_make_grid_and_labels.py first.", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(model_path):
        print("Missing model. Run 06_train_model_v0.py first.", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(labels_csv)
    pack = joblib.load(model_path)
    model = pack["model"]
    feat_cols = pack["features"]

    # Ensure seasonal cols exist (reuse v0 feature creator logic quickly)
    if "doy_sin" not in df.columns or "doy_cos" not in df.columns:
        # simplest: merge from train_v0 if present
        train_path = "data/train_v0.csv"
        if os.path.exists(train_path):
            t = pd.read_csv(train_path)[["grid_id", "doy_sin", "doy_cos"]]
            df = df.merge(t, on="grid_id", how="left")
        else:
            print("Missing doy features. Run 05_make_features_v0.py first.", file=sys.stderr)
            sys.exit(1)

    X = df[feat_cols].values
    df["prob"] = model.predict_proba(X)[:, 1]

    out_path = "data/forecast_grid_v0.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved forecast grid -> {out_path}")

if __name__ == "__main__":
    main()
