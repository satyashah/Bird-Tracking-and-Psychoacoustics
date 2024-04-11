import pandas as pd
import matplotlib.pyplot as plt

csv_path = "data/canary_3khz_2024-04-11_10-11-49.csv"

df = pd.read_csv(csv_path)

print(df)

df['color'] = df.apply(lambda row: 'blue' if row['tone'] else ('green' if row['sound'] else ('red' if row['tone'] and row['sound'] else 'black')), axis=1)

# Plotting
plt.figure(figsize=(10, 6))
for color in df['color'].unique():
    df_color = df[df['color'] == color]
    plt.scatter(df_color['time'], df_color['angle'], color=color, label=color)

statistics = df.groupby('color').agg({
    'angle': ['mean', 'max', 'min', 'std']
})

print(statistics)

plt.xlabel('Time')
plt.ylabel('Angle')
plt.legend()
plt.show()