import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
import joblib

def main():
    path = "data/train_v0.csv"
    if not os.path.exists(path):
        print("Missing data/train_v0.csv. Run 05_make_features_v0.py first.", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(path)

    feat_cols = ["lat", "lon", "doy_sin", "doy_cos"]
    if not set(feat_cols + ["label"]).issubset(df.columns):
        print("Missing required columns in train_v0.csv", file=sys.stderr)
        sys.exit(1)

    X = df[feat_cols].values
    y = df["label"].astype(int).values

    # NOTE: With only one day you can’t train; you’ll want many days later.
    # This script assumes train_v0.csv will eventually be appended across dates.
    if len(set(y)) < 2:
        print("Need both 0s and 1s in labels to train. Use more days.", file=sys.stderr)
        sys.exit(1)

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    clf = LogisticRegression(max_iter=1000, class_weight="balanced")
    clf.fit(Xtr, ytr)

    p = clf.predict_proba(Xte)[:, 1]
    brier = brier_score_loss(yte, p)
    auc = roc_auc_score(yte, p)

    os.makedirs("models", exist_ok=True)
    model_path = "models/nadocast_v0_logreg.joblib"
    joblib.dump({"model": clf, "features": feat_cols}, model_path)

    print(f"Saved model -> {model_path}")
    print(f"Holdout Brier: {brier:.6f} | AUC: {auc:.4f}")

if __name__ == "__main__":
    main()
