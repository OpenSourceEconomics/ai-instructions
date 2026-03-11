# ML vs Econometrics

**Econometrics** (statsmodels): causal inference, hypothesis testing

**ML** (scikit-learn): prediction

Critical rules:

- Never interpret ML parameters causally
- Never skip train/test split for prediction tasks
- Never evaluate on training data
- Use cross-validation for hyperparameter tuning
- Reserve test set for final evaluation only

```python
# Statsmodels
import statsmodels.formula.api as smf

results = smf.ols("y ~ x1 + x2", data=df).fit(cov_type="HC1")

# Scikit-learn
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)
```
