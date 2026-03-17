# Plotting (Plotly)

**Use Plotly exclusively.** Do not use matplotlib, seaborn, or other plotting libraries.

```python
import plotly.express as px
import plotly.io as pio

pio.templates.default = "plotly_dark"
pd.options.plotting.backend = "plotly"
```

Key principles:

1. Show the data clearly
1. Remove clutter (unnecessary gridlines, borders)
1. Use facets to avoid spaghetti charts
1. Use grey as default, accent colors for emphasis
1. Label directly on plot when possible
