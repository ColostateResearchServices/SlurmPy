from jinja2 import Environment, FileSystemLoader
import os
import base64

# Load Jinja2 template
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('report_template.html')

# Define the directory containing the plots
report_directory = 'outputs/12_01_23_12_31_23'

# Function to encode image to Base64
def encode_image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Prepare plot details
plots = [
    {
        'title': 'Total Usage Overview',
        'img_data': encode_image_to_base64(os.path.join(report_directory, 'csu_ucb_rmacc.png')),
        'description': 'This pie chart shows the breakdown of total usage among CSU, UCB, and RMACC users in the Alpine cluster.'
    },
    {
        'title': 'CSU Account Usage: General vs. Projects',
        'img_data': encode_image_to_base64(os.path.join(report_directory, 'csu_general_vs_projects.png')),
        'description': 'This pie chart compares the usage of \'csu-general\' and \'csu-projects\'. It\'s aimed at understanding the distribution between general and project-specific resource usage within CSU.'
    },
    {
        'title': 'Top 10 Users in CSU-Projects',
        'img_data': encode_image_to_base64(os.path.join(report_directory, 'top_10_csu_projects_users.png')),
        'description': 'This plot highlights the top 10 users within the \'csu-projects\' account, showcasing the primary users and their respective usage proportions.'
    },
    {
        'title': 'Top 10 Users in CSU-General',
        'img_data': encode_image_to_base64(os.path.join(report_directory, 'top_10_csu_general_users.png')),
        'description': 'This pie chart presents the top 10 users of the \'csu-general\' account, offering insights into which users are the most active in general usage categories.'
    },
    {
        'title': 'CSU Usage Trend: General vs. Projects',
        'img_data': encode_image_to_base64(os.path.join(report_directory, 'csu_gen_vs_proj_15int_2_days.png')),
        'description': 'This line graph illustrates the usage trends of \'csu-general\' and \'csu-projects\' over the past months, providing a comparative view of the usage patterns between these two account types.'
    },
    {
        'title': 'Trend Analysis for Newly Approved Projects',
        'img_data': encode_image_to_base64(os.path.join(report_directory, 'new_csu_projects_accounts_usage_1int_30_days.png')),
        'description': 'A line graph showing the usage trend of recently approved CSU projects. This plot is essential for assessing the effectiveness of project allocation and initial usage patterns.'
    },
    {
        'title': 'User Efficiency Metrics',
        'img_data': encode_image_to_base64(os.path.join(report_directory, 'efficiency_metrics.png')),
        'description': 'Bar graphs representing CPU and memory efficiency metrics for selected users, based on data from the \'seff\' tool. This analysis is crucial for understanding how efficiently cluster resources are being utilized.'
    },
    {
        'title': 'Users Exceeding Quota in CSU-General',
        'img_data': encode_image_to_base64(os.path.join(report_directory, 'csu_general_users_using_over_quota_30_days_limit_40000.png')),
        'description': 'This horizontal bar graph displays users whose usage exceeds the set quota in the \'csu-general\' account, highlighting areas where resource consumption may need to be managed more effectively.'
    },
    {
        'title': 'Project Allocation Trend Over the Last 6 Months',
        'img_data': encode_image_to_base64(os.path.join(report_directory, 'allocation_trend.png')),
        'description': 'A visual representation showing the trend in the total number of projects allocated over the last six months, providing insights into the allocation rate and potential demand trends in project resources.'
    }
]

# Render the template with plot details
html_output = template.render(plots=plots)

# Save the rendered HTML to a file
html_report_file = f"{report_directory}/usage_report_csu.html"
with open(html_report_file, 'w') as file:
    file.write(html_output)
    print(f"HTML report created: {html_report_file}")
