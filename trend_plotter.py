import datetime
import matplotlib.pyplot as plt
import pandas as pd
from cu_slurmtools_py import SReport
import numpy as np
from matplotlib import patheffects as path_effects

OUTPUT_DIR = 'outputs/'


class TrendPlotter:
    def __init__(self, intervals, interval_size, user=None, title='Usage Trend', account='csu-general', directory_name='untitled', filename_prefix='usage_trends', last_date=None, verbose=False):
        self.intervals = intervals  # Number of intervals
        self.interval_size = interval_size  # Size of each interval (in days)
        self.users = [u.strip() for u in (user or "").split(',')]  # List of users
        self.title = title  # Title for the plot
        self.directory_name = directory_name  # Directory name for the output file
        self.verbose = verbose
        self.sreport = SReport(verbose=self.verbose, out_dir=directory_name)  # Initialize SReport instance
        self.accounts = [a.strip() for a in account.split(',')]  # List of accounts
        self.filename_prefix = filename_prefix  # Prefix for the output filename
        self.max_users = 0  # To store maximum number of users
        if last_date is None:
            self.last_date = datetime.datetime.now()  # Current time
        else:
            self.last_date = last_date

    # Method to fetch the data for a given interval and return the usage
    def get_interval_data(self, start_date, end_date):
        start = start_date.strftime('%m/%d/%y')  # Format start date
        end = end_date.strftime('%m/%d/%y')  # Format end date

        usages = {}  # Dictionary to store usage for each account and user
        for account in self.accounts:  # Loop over each account
            for user in self.users:  # Loop over each user
                # Fetch data using SReport instance
                self.sreport.cluster_report('AccountUtilizationByUser', options=[f'Accounts={account}', f'start={start}', f'end={end}'])

                df = self.sreport.get_report_data()  # Get report data as dataframe
                try:
                    # Check if user is specified, else return total usage
                    if user:
                        matching_rows = df[df['Login'].str.contains(user, na=False)]  # Rows that match the user
                        usage = matching_rows['Used'].sum()  # Calculate total usage

                        # Update max_users if we found more matching users than before
                        self.max_users = max(self.max_users, matching_rows.shape[0])
                    else:
                        usage = df[df['Login'].apply(lambda x: x is np.nan or x == '')]['Used'].sum()  # Total usage
                    if self.verbose:
                        print(f"Total usage for {account} {user if user else ''} from {start} to {end}: {usage}")
                    usages[f'{account}_{user if user else "total"}'] = usage  # Store usage in dictionary
                except KeyError:
                    if self.verbose:
                        print(f"No data found for {account} {user if user else ''}")
                    usages[f'{account}_{user if user else "total"}'] = 0

        return usages  # Return the usage dictionary

    # Method to generate trend data
    def generate_trends(self):
        trends = {f'{account}_{user if user else "total"}': [] for account in self.accounts for user in self.users}  # Dictionary to store trends data for each account and user
        for i in range(self.intervals):  # Loop over each interval
            # Calculate start and end dates for each interval
            end_date = self.last_date - datetime.timedelta(days=self.interval_size*i)
            start_date = self.last_date - datetime.timedelta(days=self.interval_size*(i+1))

            usages = self.get_interval_data(start_date, end_date)  # Get the usage data for the interval
            for account_user, usage in usages.items():  # Loop over each account and user
                trends[account_user].append({'date': end_date, 'usage': usage})  # Append the usage data to the trends data

        self.trends_df = {account_user: pd.DataFrame(trend_data) for account_user, trend_data in trends.items()}  # Convert trends data to pandas dataframes

    def plot_single_interval_bar(self, trends_df):
        categories = []
        usages = []
        labels = []

        # Use a colormap that provides better contrast
        colors = plt.cm.tab20c(np.linspace(0, 1, len(trends_df)))

        for account_user, trends in trends_df.items():
            categories.append(account_user)
            usages.append(trends['usage'][0])
            labels.append(trends['date'][0].strftime('%Y-%m-%d'))

        # Plot bars with colors and labels
        for idx, (category, usage) in enumerate(zip(categories, usages)):
            plt.bar(category, usage, color=colors[idx], label=category.replace('_', ' ').title())

            # Annotate the bar with the project name if usage is non-zero
            if usage > 0:
                plt.text(category, 0, category.split('_')[0], ha='center', va='bottom', rotation='vertical', fontsize=9, color='white',
                         path_effects=[path_effects.Stroke(linewidth=1, foreground='black'), path_effects.Normal()],
                         weight='bold')

        plt.xticks(categories, labels)  # Setting X-axis labels to the actual dates
        plt.grid(False)  # Remove grid

    def plot_trends(self):
        plt.figure(figsize=(12, 6))  # Create a new figure

        # Flag to identify if the trend is for a single interval
        single_interval = any([len(trends['date']) == 1 for trends in self.trends_df.values()])

        if single_interval:
            self.plot_single_interval_bar(self.trends_df)
            plt.xticks([])  # Remove x-axis ticks
            plt.xlabel('')  # Remove x-axis label since we have only one date
        else:
            for account_user, trends in self.trends_df.items():
                plt.plot(trends['date'], trends['usage'], marker='o', linewidth=2, label=account_user.replace('_', ' ').title())
            plt.xlabel('Date')  # Set x-axis label only for multiple intervals

        plt.title(self.title)  # Set title
        plt.ylabel('Total Usage')  # Set y-axis label
        plt.subplots_adjust(bottom=0.20, right=0.75)  # Adjust subplot params
        plt.grid(axis='y')  # Display horizontal grid lines only

        # Place legend outside the plot area
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        filename = f"{self.directory_name}/{self.filename_prefix}_{self.intervals}int_{self.interval_size}_days.png"  # Construct filename
        check_directory(filename)  # Check if directory exists
        plt.savefig(filename, bbox_inches='tight')  # Save plot to file with adjusted bounding box
        print(f"Saved trend plot to {filename}")  # Print output file path


def check_directory(filename, verbose=False):
    if verbose:
        print(f"Checking directory for {filename}")
    import os
    directory = os.path.dirname(filename)
    if verbose:
        print(f"Directory: {directory}")
    if not os.path.exists(directory):
        os.makedirs(directory)
        if verbose:
            print(f"Created directory {directory}")
    else:
        if verbose:
            print(f"Directory {directory} already exists")
