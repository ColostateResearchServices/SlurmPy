from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd
import datetime

def read_project_data(csv_string):
    df = pd.read_csv(csv_string)
    # Add the 'Allocation' column
    df['Allocation'] = df['Project Name'].apply(lambda x: f"{x}_alpine1")
    
    # Handle any missing values
    df.fillna("-", inplace=True)
    
    # Print the unique values of the 'Allocation' column for verification
    # print("Unique Allocations in project_df:", df['Allocation'].unique())
    
    return df

def plot_project_allocation_trend(rcamp_data, months=6, filename="allocation_trend.png"):
    """
    Plot a time-series line graph depicting the number of projects allocated in the last N months.
    
    :param rcamp_data: DataFrame containing rcamp project details.
    :param months: Number of months to be considered for the plot.
    """
    # Convert 'Start Date' column to datetime format
    rcamp_data['Start Date'] = pd.to_datetime(rcamp_data['Start Date'], errors='coerce')
    
    # Filter data for the last N months
    end_date = datetime.datetime.today()
    start_date = end_date - timedelta(days=30*months)
    mask = (rcamp_data['Start Date'] >= start_date) & (rcamp_data['Start Date'] <= end_date)
    filtered_data = rcamp_data[mask]
    
    # Group by month and count number of projects
    monthly_counts = filtered_data.groupby(filtered_data['Start Date'].dt.to_period("M")).size()
    
    # Plotting
    plt.figure(figsize=(10, 6))
    monthly_counts.plot(kind='line', marker='o')
    plt.title(f'Number of Projects Added Each Month (Last {months} Months)')
    plt.xlabel('Month')
    plt.ylabel('Number of Projects')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename)
    print(f"Saved file {filename}")
