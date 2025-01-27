from cu_slurmtools_py import SReport, SacctTools, SeffWrapper
from pie_chart_plotter import PieChartPlotter
import pandas as pd
from horizontal_bar_plot import HorizontalBarPlotLimit
from trend_plotter import TrendPlotter
import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
from util_functions import *
import numpy as np

run_steps = [1, 2, 3, 4, 5, 6, 7, 8]
# run_steps = [6]

num_days = 30

# Manual start time
start = '12/01/23'  # Format: 'mm/dd/yy'
end = (datetime.datetime.strptime(start, '%m/%d/%y') + datetime.timedelta(days=num_days)).strftime('%m/%d/%y')

# Automatic start time
# start = (datetime.datetime.now() - datetime.timedelta(days=num_days)).strftime('%m/%d/%y')
# end = datetime.datetime.now().strftime('%m/%d/%y')

verbose = False  # verbose saves csv data for all plots
directory_name = f"outputs/{start.replace('/', '_')}_{end.replace('/', '_')}"
print(f"Report directory: {directory_name}")
sreport = SReport(verbose=verbose, out_dir=directory_name)  # Initialize SReport instance
rcamp_df = read_project_data("project_data.csv")
active_users=[] # for efficiency calculation

step = 1
if step in run_steps:
    # 1. CSU's Total Usage Overview
    """ Pie-Chart: Breakdown of total usage among different users of the Alpine cluster: CSU, CU, RMACC. """
    sreport.cluster_report('AccountUtilizationByUser', options=['Accounts=csu,ucb,rmacc', f'start={start}', f'end={end}'])
    df = sreport.get_report_data(only_institutions=True)  # Get users report data as dataframe
    plotter = PieChartPlotter(df, column='Account', usage_col='Used', top_n=10, filename=f'{directory_name}/csu_ucb_rmacc.png', title='Share of CSU, UCB, RMACC')
    plotter.plot()

step = 2
if step in run_steps:
    # 2. Comparison between CSU Accounts: csu-general vs. csu-projects
    """Usage Breakdown: Pie-chart representing the percentage usage of csu-general versus csu-projects.
    Objective Analysis: Insights into efforts promoting higher "csu-projects" usage for detailed resource tracking.
    """
    sreport.cluster_report('AccountUtilizationByUser', options=['Accounts=csu-general,csu-projects', f'start={start}', f'end={end}'])
    df = sreport.get_report_data(exclude_users=True, only_csu_general_and_projects=True)  # Get users report data as dataframe
    plotter = PieChartPlotter(df, column='Account', usage_col='Used', top_n=10, filename=f'{directory_name}/csu_general_vs_projects.png', title='Share of CSU-General and CSU-Projects')
    plotter.plot()

step = 3
if step in run_steps:
    # 3. Top Users Analysis
    """CSU-Projects: List of top users and their respective usage.
    CSU-General: List of top users and their respective usage."""

    # 3.1 CSU-Projects
    """Pie-chart representing the percentage usage of top 10 csu-projects users.
    Objective Analysis: Insights into efforts promoting higher "csu-projects" usage for detailed resource tracking."""
    sreport = SReport(verbose=verbose, out_dir=directory_name)  # Initialize SReport instance
    sreport.cluster_report('AccountUtilizationByUser', options=['Accounts=csu-projects', f'start={start}', f'end={end}'])
    df = sreport.get_report_data(exclude_accounts=True)  # Get users report data as dataframe
    # print("Unique Accounts in df:", df['Account'].unique())
    plotter = PieChartPlotter(df, column='Account', usage_col='Used', top_n=10, filename=f'{directory_name}/top_10_csu_projects_users.png', title='Top 10 CSU-Projects Users', table_cols=['Login'], project_df=rcamp_df)
    plotter.plot()

    # # 3.2 CSU-General
    """Pie-chart representing the percentage usage of top 10 csu-general users.
    Objective Analysis: Insights into efforts promoting higher "csu-general" usage for detailed resource tracking."""
    sreport = SReport(verbose=verbose, out_dir=directory_name)  # Initialize SReport instance
    sreport.cluster_report('AccountUtilizationByUser', options=['Accounts=csu-general', f'start={start}', f'end={end}'])
    df = sreport.get_report_data(exclude_accounts=True)  # Get users report data as dataframe
    plotter = PieChartPlotter(df, column='Login', usage_col='Used', top_n=10, filename=f'{directory_name}/top_10_csu_general_users.png', title='Top 10 CSU-General Users')
    plotter.plot()

step = 4
if step in run_steps:

    # 4 Usage Trend Over Time
    """
    Overall Trend Plot: Line graph showing CSU's overall usage trend over past months.
    Breakdown Trend Plot: Comparative line graphs for csu-general and csu-projects over the past months.
    """

    trend_plotter = TrendPlotter(intervals=15, interval_size=2, account='csu-general,csu-projects', filename_prefix="csu_gen_vs_proj",
                                 directory_name=directory_name, last_date=datetime.datetime.strptime(end, '%m/%d/%y'), verbose=False)  # for plotting both csu-general and csu-projects usage on the same plot
    trend_plotter.generate_trends()
    trend_plotter.plot_trends()

step = 5
if step in run_steps:
    # 5. Usage Trends for Recently Allocated Projects
    """
    Trend Analysis: Line graph showing usage trend for recently approved projects to assess project allocation effectiveness.
    """
    latest_account = 77
    last_10_accounts_made = [f"csu{n}_alpine1" for n in range(latest_account-10, latest_account+1)]
    trend_plotter = TrendPlotter(intervals=1, interval_size=30, account=','.join(last_10_accounts_made),
                                 filename_prefix='new_csu_projects_accounts_usage', directory_name=directory_name, last_date=datetime.datetime.strptime(end, '%m/%d/%y'), verbose=False)  # for csu-projects usage
    trend_plotter.generate_trends()
    trend_plotter.plot_trends()

step = 6
if step in run_steps:
    # 6. Efficiency Metrics
    """ Job Efficiency: Analysis based on CPU and memory efficiencies from the seff tool. """
    
    # Assume active_users is the list of usernames
    active_users = ["kamil@colostate.edu", "lindsval@colostate.edu", "jlamb1@colostate.edu", "delee@colostate.edu", "gdvieira@colostate.edu"]

    # Initialize the SacctTools and SeffWrapper
    sacct_tools = SacctTools()
    seff_wrapper = SeffWrapper()

    user_cpu_efficiencies = {}
    user_mem_efficiencies = {}

    for user in active_users:
        # Incorporate the start and end dates to the SacctTools command arguments
        df = sacct_tools.get_data(command_args=["-u", user, "--starttime", start, "--endtime", end])

        # List of job IDs for the current user
        job_ids = df["JobID"].tolist()

        # Lists to store efficiency metrics and runtimes for each job
        cpu_effs = []
        mem_effs = []
        runtimes = []

        for job_id in job_ids:
            print(f"Checking efficiency for job {job_id}")
            eff_data = seff_wrapper.fetch_efficiency(job_id)

            # Store the efficiency values; converting them from string to float
            cpu_effs.append(float(eff_data["CPU Efficiency"].replace("%", "")))
            mem_effs.append(float(eff_data["Memory Efficiency"].replace("%", "")))
            
            # Extract and convert job's wall-clock time to seconds
            wall_time = eff_data["Job Wall-clock time"]
            # print(f"wall_time:{wall_time}")

            total_seconds = wall_time
            runtimes.append(total_seconds)

        # Compute the weighted average efficiencies for the user
        if sum(runtimes) != 0:
            user_cpu_efficiencies[user] = np.average(cpu_effs, weights=runtimes)
            user_mem_efficiencies[user] = np.average(mem_effs, weights=runtimes)

    # Plotting
    users = list(user_cpu_efficiencies.keys())
    cpu_efficiency_vals = list(user_cpu_efficiencies.values())
    mem_efficiency_vals = list(user_mem_efficiencies.values())

    plt.figure(figsize=(15, 5))

    # CPU Efficiency plot
    plt.subplot(1, 2, 1)
    plt.bar(users, cpu_efficiency_vals, color='blue')
    plt.xlabel('Users')
    plt.ylabel('CPU Efficiency (%)')
    plt.title('Average CPU Efficiency')
    plt.xticks(rotation=45, ha="right")

    # Memory Efficiency plot
    plt.subplot(1, 2, 2)
    plt.bar(users, mem_efficiency_vals, color='green')
    plt.xlabel('Users')
    plt.ylabel('Memory Efficiency (%)')
    plt.title('Average Memory Efficiency')
    plt.xticks(rotation=45, ha="right")
    # plt.ylim(100)

    plt.tight_layout()
    plt.savefig(f"{directory_name}/efficiency_metrics.png")
    print(f"Saved figure {directory_name}/efficiency_metrics.png")

step = 7
if step in run_steps:
    # 7. Usage Above Quota
    """Usage Above Quota: Horizontal bar graph showing users with usage above quota for csu-general and csu-projects."""
    sreport = SReport(verbose=verbose, out_dir=directory_name)  # Initialize SReport instance
    # start date is 28 days ago and end date is today
    num_days_for_quota = num_days
    # start = (datetime.datetime.now() - datetime.timedelta(days=num_days_for_quota)).strftime('%m/%d/%y')
    # end = datetime.datetime.now().strftime('%m/%d/%y')
    sreport.cluster_report('AccountUtilizationByUser', options=['Accounts=csu-general', f'start={start}', f'end={end}'])
    df = sreport.get_report_data(exclude_accounts=True)  # Get users report data as dataframe
    limit = 40000
    plotter = HorizontalBarPlotLimit(df, column='Login', usage_col='Used',
                                     filename=f'{directory_name}/csu_general_users_using_over_quota_{num_days_for_quota}_days_limit_{limit}.png', title=f'csu-general Users With Usage Above Quota ({num_days_for_quota} days)', limit=limit)
    plotter.plot()

    # Run the function if step 8
step = 8
if step in run_steps:
    # 8. Project Allocation Trend
    """Show the total number of allocated projects for the last 6 months"""
    plot_project_allocation_trend(rcamp_df, months=6, filename=f'{directory_name}/allocation_trend.png')

