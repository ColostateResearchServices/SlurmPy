import matplotlib.pyplot as plt
import pandas as pd

class HorizontalBarPlotLimit:
    def __init__(self, df, column, usage_col, filename, title=None, limit=100000):
        self.df = df
        self.column = column
        self.usage_col = usage_col
        self.filename = filename
        self.limit = limit
        self.title = title + f' (Limit: {self.limit})'

    def plot(self):
        # Convert usage to numeric
        self.df[self.usage_col] = pd.to_numeric(self.df[self.usage_col], errors='coerce')
        
        # Filter users who have used more than the limit
        df_filtered = self.df[self.df[self.usage_col] > self.limit]

        # Sort users by usage
        df_filtered = df_filtered.sort_values(self.usage_col)

        # if df_filtered is empty, print message and return
        if df_filtered.empty:
            print(f"No users found with usage above {self.limit}")
            return

        # Plot the bar chart
        plt.figure(figsize=(10, 8))
        bars = plt.barh(df_filtered[self.column], df_filtered[self.usage_col], color='skyblue')
        plt.xlabel('Usage')
        plt.ylabel('Users')
        plt.title(self.title)
        
        # Plot the limit line
        plt.axvline(x=self.limit, color='r', linestyle='--', label=f'Limit: {self.limit}')
        plt.legend()
        
        # Add data labels
        for bar in bars:
            plt.text(bar.get_width() + bar.get_width()*0.01, bar.get_y() + bar.get_height()/2, 
                     f'{bar.get_width():.0f}', va='center', ha='left')
        
        # Extend the xlim of the plot
        plt.xlim(0, df_filtered[self.usage_col].max() * 1.1)

        plt.tight_layout()
        plt.savefig(self.filename)
        print(f"Saved bar plot to {self.filename}")
