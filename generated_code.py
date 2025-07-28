import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO

# Step 1: Load the CSV
df = pd.read_csv("matched_table.csv")

# Step 2: Print basic metadata
print("Shape:", df.shape)
print("Columns:", df.columns.tolist())
print("First 3 Rows:\n", df.head(3))

# Step 3: Clean numeric columns
for col in ['Worldwide gross']:
    df[col] = df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Step 4: Drop nulls in numeric columns
df = df.dropna(subset=['Worldwide gross'])

# Task 1: How many $2 bn movies were released before 2020?
count_2bn_movies = len(df[(df['Worldwide gross'] >= 2000000000) & (df['Year'] < 2020)])

# Task 2: Which is the highest grossing film in the world?
highest_grossing_film = df.loc[df['Worldwide gross'].idxmax(), 'Title']

# Task 3: What's the correlation between Rank and Peak?
correlation_rank_peak = df['Rank'].corr(df['Peak'])

# Task 4: Draw a scatterplot of Rank and Peak along with a dotted red regression line through it
plt.figure(figsize=(10, 6))
sns.regplot(x='Rank', y='Peak', data=df, scatter_kws={'color': 'blue'}, line_kws={'color': 'red', 'linestyle': '--'})
plt.title('Rank vs Peak')
plt.xlabel('Rank')
plt.ylabel('Peak')
plt.grid()
plt.tight_layout()

# Save the plot to a BytesIO object and encode it as base64
buf = BytesIO()
plt.savefig(buf, format='png')
buf.seek(0)
plot_data = base64.b64encode(buf.read()).decode('utf-8')
base64_image = f"data:image/png;base64,{plot_data}"

# Combine results
result = {
    "count_2bn_movies": count_2bn_movies,
    "highest_grossing_film": highest_grossing_film,
    "correlation_rank_peak": correlation_rank_peak,
    "scatterplot": base64_image
}

# Print the result
import json
print(json.dumps(result))