from cu_slurmtools_py import SacctTools, SLURMTools, SReport
from pie_chart_plotter import PieChartPlotter
import pandas as pd

# Goal: Get CSU users usage report
# 1: Get top users and plot pie-chart 
# 2: Get top accounts and plot pie-chart
# 3: Get csu-general and projects share and plot pie chart


slurm_tools = SLURMTools(verbose=True)

csu_users_df = slurm_tools.suacct('csu', days=365, only_csu_general=False)
print(csu_users_df.head())
plotter = PieChartPlotter(csu_users_df, 'Login', 'Used', 10, 'outputs/top_10_csu_users.png', title='Top 10 CSU Users by SU Used')
plotter.plot()

csu_general_users_df = slurm_tools.suacct('csu', days=365, only_csu_general=True)
print(csu_general_users_df.head())
plotter = PieChartPlotter(csu_general_users_df, 'Login', 'Used', 10, 'outputs/top_10_csu_general_users.png', title='Top 10 csu-general Users by SU Used')
plotter.plot()
