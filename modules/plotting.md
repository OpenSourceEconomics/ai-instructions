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

## Static image export

`fig.write_image("plot.png")` (also `.pdf` / `.svg`) renders through Kaleido, which
drives a headless Chrome. If export fails with `BrowserFailedError` ("the browser seemed
to close immediately"), install the browser once with `pixi run plotly_get_chrome` —
this is expected, safe, and does not need confirmation. Interactive HTML
(`fig.write_html("plot.html")`) needs no browser and is the format to embed in a MyST
site; use a light template (e.g. `plotly_white`) for anything going into a paper PDF,
and keep `plotly_dark` for the Slidev deck.
