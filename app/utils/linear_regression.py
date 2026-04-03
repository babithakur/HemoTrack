import numpy as np

class SimpleLinearRegression:
    def __init__(self):
        self.coef_ = None  # slope
        self.intercept_ = None

    def fit(self, X, y):
        # Convert to numpy arrays
        X = np.array(X).flatten()
        y = np.array(y)

        # Mean values
        x_mean = np.mean(X)
        y_mean = np.mean(y)

        # Calculate slope (m)
        numerator = np.sum((X - x_mean) * (y - y_mean))
        denominator = np.sum((X - x_mean) ** 2)

        self.coef_ = numerator / denominator

        # Calculate intercept (b)
        self.intercept_ = y_mean - self.coef_ * x_mean

    def predict(self, X):
        X = np.array(X).flatten()
        return self.coef_ * X + self.intercept_
    
    def mse(self, X, y):
        y = np.array(y)
        y_pred = self.predict(X)
        return np.mean((y - y_pred) ** 2)

    def r2_score(self, X, y):
        y = np.array(y)
        y_pred = self.predict(X)

        ss_total = np.sum((y - np.mean(y)) ** 2)
        ss_residual = np.sum((y - y_pred) ** 2)

        return 1 - (ss_residual / ss_total)