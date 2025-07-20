import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from utils.base64_tools import fig_to_base64


def create_scatterplot(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.regplot(
        data=df, x="Rank", y="Peak",
        marker="o", line_kws={"color": "red", "linestyle": "dotted"}, ax=ax
    )
    ax.set_title("Rank vs Peak with Regression Line")
    fig.tight_layout()

    return fig_to_base64(fig)


def plot_delay_by_year(delay_data):
    df = pd.DataFrame(delay_data, columns=["Year", "Delay"])
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.regplot(
        data=df, x="Year", y="Delay",
        marker="o", line_kws={"color": "red", "linestyle": "dotted"}, ax=ax
    )
    ax.set_title("Average Delay (Days) by Year")
    fig.tight_layout()

    return fig_to_base64(fig)
