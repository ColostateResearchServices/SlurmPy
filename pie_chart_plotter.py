import matplotlib.pyplot as plt
import pandas as pd

class PieChartPlotter:
    def __init__(self, df, column, usage_col, top_n, filename, title=None, display_values=True, min_font_size=8, max_font_size=36, figure_size=(18,12), table_cols=None, project_df=None):
        self.df = df
        self.column = column
        self.usage_col = usage_col
        self.top_n = top_n
        self.filename = filename
        self.display_values = display_values
        self.min_font_size = min_font_size
        self.max_font_size = max_font_size
        self.figure_size = figure_size
        self.title = title
        self.table_cols = table_cols
        self.project_df = project_df

    def autopct_format(self, values):
        def my_format(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return ('{p:.2f}%\n({v:d})' if self.display_values else '{p:.2f}%').format(p=pct,v=val)
        return my_format

    def adjust_font_size(self, autotexts):
        for autotext in autotexts:
            percentvalue = float(autotext.get_text().split('%')[0])
            if percentvalue < 1:
                autotext.set_fontsize(self.min_font_size)
            elif percentvalue < 5:
                autotext.set_fontsize(self.min_font_size + (self.max_font_size - self.min_font_size) // 5) 
            elif percentvalue > 5 and percentvalue < 50:
                autotext.set_fontsize(self.min_font_size + 2 * (self.max_font_size - self.min_font_size) // 5)
            elif percentvalue > 50:
                autotext.set_fontsize(self.max_font_size)

    def plot(self):
        # Usual plotting procedure
        self.df[self.usage_col] = pd.to_numeric(self.df[self.usage_col], errors='coerce')
        self.df = self.df[self.df[self.usage_col] > 0]
        self.df = self.df.sort_values(self.usage_col, ascending=False).head(self.top_n)
        
        plt.figure(figsize=self.figure_size)
        patches, texts, autotexts = plt.pie(self.df[self.usage_col], autopct=self.autopct_format(self.df[self.usage_col]), startangle=90, pctdistance=0.75, counterclock=False)
        plt.legend(patches, self.df[self.column], loc="upper right", fontsize=16, bbox_to_anchor=(1.3, 1))
        self.adjust_font_size(autotexts)
        
        # Title configuration
        if self.title:
            plt.title(self.title, fontsize=30)
        else:
            plt.title(f'Top {self.top_n} Users by {self.usage_col}', fontsize=30)

        # Merge and display the table if project_df is provided
        if self.project_df is not None:
            self.df = pd.merge(self.df, self.project_df[['Allocation', 'Project Description']], left_on='Account', right_on='Allocation', how='left')
            table_data = self.df[['Account', 'Project Description'] + self.table_cols].head(self.top_n).values.tolist()
            
            ax = plt.gca()
            ax.axis('off')
            
            # Creating the table
            table = ax.table(cellText=table_data, colLabels=['Allocation', 'Project Description'] + self.table_cols, cellLoc='center', loc='bottom')
            # Adjust cell widths based on content
            cell_widths = []
            for col_id, column in enumerate(table_data[0]):
                max_width = max([len(str(row[col_id])) for row in table_data])
                cell_widths.append(max_width)
        
            # Wrap long text and adjust cell width
            col_max_width = 30  # maximum width for a cell
            for i, cell_width in enumerate(cell_widths):
                for cell in table[0, i].get_text().get_text().splitlines():
                    if len(cell) > col_max_width:
                        cell.set_text("\n".join(wrap(cell, col_max_width)))
                table.auto_set_column_width(i)

            # Adjusting the table position to give it a top/bottom margin
            table.auto_set_font_size(False)
            table.set_fontsize(13)  # Set fontsize to fit the text
            table.scale(1, 1.5)  # Increase the vertical cell size to give more space

        # Save the plot
        plt.tight_layout()
        self.check_directory()
        plt.savefig(self.filename)
        print(f"Saved pie chart to {self.filename}")
    
    def check_directory(self):
        import os
        directory = os.path.dirname(self.filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory {directory}")
        else:
            print(f"Directory {directory} already exists")
