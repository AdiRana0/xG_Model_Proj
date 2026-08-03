from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
import joblib
import json
import pandas as pd


# --- RETRIEVE FEATURES/LABEL ---

X, y = joblib.load('data/Xy.pkl')


# --- TRAIN/TEST SPLIT ---

X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8, random_state=26, stratify=y)
# train test split: 80/20

# print(y_train.mean(), y_test.mean()) 
# sanity check; both should be ~10% for similar percentage of goals in train and test


# --- MODEL 1: Logistic Regression ---
# Scale distance/angle features down; unnecessary but good practice

sc = StandardScaler()
X_train_sc = X_train.copy()
X_test_sc = X_test.copy()

X_train_sc[['distance', 'angle']] = sc.fit_transform(X_train[['distance', 'angle']])
X_test_sc[['distance', 'angle']] = sc.fit_transform(X_test[['distance', 'angle']])


LR = LogisticRegression(max_iter=1000)
LR.fit(X_train_sc, y_train)

LR_probabilities = LR.predict_proba(X_test_sc)[:,1]

print("LR — Log Loss:", log_loss(y_test, LR_probabilities))
print("LR — AUC:", roc_auc_score(y_test, LR_probabilities))


# --- MODEL 2: XGBoost
# Tuned XGB model; uses best combo of following parameters, derived using grid search

parameter_grid = {
    'max_depth': [4],
    'learning_rate': [0.05, 0.075, 0.1, 0.125, 0.15],
    'n_estimators': [50],
    'min_child_weight': [1]
}

XGB_est = XGBClassifier(eval_metric='logloss', random_state=26)

grid_search = GridSearchCV(estimator=XGB_est, param_grid=parameter_grid, scoring='neg_log_loss', cv=5, n_jobs=-1, verbose=1)

grid_search.fit(X_train, y_train)

print("Best parameters:", grid_search.best_params_)
print("Best CV log loss:", -grid_search.best_score_)

XGB = grid_search.best_estimator_

XGB_probabilities = XGB.predict_proba(X_test)[:, 1]

print("XGBoost — Log Loss:", log_loss(y_test, XGB_probabilities))
print("XGBoost — AUC:", roc_auc_score(y_test, XGB_probabilities))


# --- SAVE MODEL ---

joblib.dump(LR, 'data/xg_model_v1.pkl')
joblib.dump(sc, 'data/scaler.pkl')

print('Model saved')
