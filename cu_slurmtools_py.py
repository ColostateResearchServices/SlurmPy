import subprocess
import csv
import os
import re
import pandas as pd
import subprocess
import time
import io
import re

OUTPUT_DIR = "outputs/"
CLUSTER_FORMAT = "Cluster,Account,Login%25,Proper Name%25,Used,Energy"  # Cluster         Account     Login     Proper Name       Used   Energy


class SLURMTools:
    def __init__(self, verbose=False):
        self.verbose = verbose
        # load the necessary modules
        # os.system("module load slurm/alpine")
        # os.system("module load slurmtools")

        # Define a dictionary with command-specific parameters
        self.command_params = {
            'suacct': {'col_names_line_num': 1, 'first_data_row_num': 2, 'separator': '\|'},
            'suuser': {'col_names_line_num': 1, 'first_data_row_num': 2, 'separator': '\|'},
            'jobstats': {'col_names_line_num': 1, 'first_data_row_num': 3, 'separator': r'\s+'},
            'levelfs': {'col_names_line_num': 1, 'first_data_row_num': 3, 'separator': r'\s+'},
            'sacct': {'separator': '\s+', 'col_names_line_num': 0, 'first_data_row_num': 2},
            # Add more commands as needed
        }

    def read_output_to_dataframe(self, output, params, filename=None):
        """
        Convert raw command output to DataFrame
        """
        output = [line for line in output if line.strip()]
        if len(output) < params['first_data_row_num'] + 1:
            print(f"Error: Not enough lines in output for command parameters: {params}")
            print("last line: ", output[-1])
            return
        try:
            column_names = re.split(params['separator'], output[params['col_names_line_num']])
        except Exception as e:
            print(f"Error processing column names: {output[params['col_names_line_num']]}")
            print(f"Error message: {str(e)}")
            return

        data_rows = []
        for i, line in enumerate(output[params['first_data_row_num']:], start=params['first_data_row_num']):
            try:
                row = re.split(params['separator'], line)
                data_rows.append(row)
            except Exception as e:
                print(f"Error processing line {i}: {line}")
                print(f"Error message: {str(e)}")
        df = pd.DataFrame(data_rows, columns=column_names)
        return df

    def execute_command(self, command):
        """
        Function to execute the command and fetch the output
        """
        try:
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
        except FileNotFoundError as e:
            print(f"Error in executing command: {command}")
            print(f"Please make sure 'module load slurm/alpine' and 'module load slurmtools' are executed")
            exit(-1)
        if error:
            print(f"Error in executing command: {command}")
            return None
        else:
            return output.decode('utf-8').split("\n")  # split the output into lines

    def read_output_to_csv(self, output, filename, params):
        """
        Convert raw command output to CSV and write to a file
        """
        # Filter out empty lines
        output = [line for line in output if line.strip()]

        # Check if there are enough lines for column names and data
        if len(output) < params['first_data_row_num'] + 1:
            print(f"Error: Not enough lines in output for command parameters: {params}")
            print("last line: ", output[-1])
            return
        try:
            # Use separator from params, strip leading/trailing pipe characters
            column_names = re.split(params['separator'], output[params['col_names_line_num']].strip('|'))
        except Exception as e:
            print(f"Error processing column names: {output[params['col_names_line_num']]}")
            print(f"Error message: {str(e)}")
            return

        data_rows = []
        for i, line in enumerate(output[params['first_data_row_num']:], start=params['first_data_row_num']):
            try:
                # Use '\|' as separator, strip leading/trailing pipe characters
                row = re.split('\|', line.strip('|'))
                data_rows.append(row)
            except Exception as e:
                print(f"Error processing line {i}: {line}")
                print(f"Error message: {str(e)}")

        # Write to CSV file
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(column_names)
            writer.writerows(data_rows)
            print(f"Output written to file: {filename}")

    def suacct(self, account_name, days=30, no_groups=True, only_groups=False, only_csu_general=False, only_projects=False, csu_general_and_projects_only=False, ignore_users='sturbek'):
        """
        Execute suacct command and parse output
        """
        command = f'suacct {account_name} {days}'
        output = self.execute_command(command)

        df = self.read_output_to_dataframe(output, self.command_params['suacct'])
        # remove accounts in comma-separated list ignore_users (Login should include the string)
        ignore_users = [u.strip() for u in ignore_users.split(',')]

        for user in ignore_users:
            df = df[~df['Login'].str.contains(user)]

        if no_groups:  # remove all rows with empty "Login" column
            df = df[df['Login'] != '']
        elif only_groups:  # remove all rows with non-empty "Login" column
            df = df[df['Login'] == '']

        if only_csu_general:  # select rows where column "Account" includes string csu-general
            df = df[df['Account'].str.contains('csu-general')]

        if only_projects:  # select rows where column "Account" does not include string csu-general
            df = df[~df['Account'].str.contains('csu-general')]

        if csu_general_and_projects_only:  # select rows where column "Account" is csu-general or csu-projects and Login is empty
            # select rows where Login is empty
            df = df[df['Login'] == '']
            df = df[(df['Account'].str.contains(' csu-general')) | (df['Account'].str.contains(' csu-projects'))]

        # If verbose is True, write DataFrame to CSV
        if self.verbose:
            filename = f'{account_name}_{days}_days_suacct.csv'
            df.to_csv(OUTPUT_DIR + filename, index=False)
            print(f"Output written to file: {filename}")

        return df

    def suuser(self, userid, days=30):
        """
        Execute suuser command and parse output
        """
        command = f'suuser {userid} {days}'
        output = self.execute_command(command)
        # Parse output into CSV format
        filename = f'{userid}_suuser.csv'
        df = self.read_output_to_dataframe(output, self.command_params['suuser'], filename)
        return df

    def jobstats(self, jobid, days=5):
        """
        Execute jobstats command and parse output
        """
        command = f'jobstats {jobid} {days}'
        output = self.execute_command(command)
        # Parse output into CSV format
        filename = f'{jobid}_jobstats.csv'
        df = self.read_output_to_dataframe(output, self.command_params['jobstats'], filename)
        return df

    def levelfs(self, userid):
        """
        Execute levelfs command and parse output
        """
        command = f'levelfs {userid}'
        output = self.execute_command(command)
        # Parse output into CSV format
        filename = f'{userid}_levelfs.csv'
        df = self.read_output_to_dataframe(output, self.command_params['levelfs'], filename)
        return df
    def seff(self, job_id):
        """
        Execute seff command and parse output
        """
        command = f'seff {job_id}'
        output = self.execute_command(command)

        # Check if output is empty
        if not output:
            return None

        # Initialize variables
        job_id = cluster = user_group = state = nodes = cores_per_node = cpu_utilized = None
        cpu_efficiency = job_wall_clock_time = memory_utilized = memory_efficiency = None

        # Parse output
        for line in output:
            if "Job ID:" in line:
                job_id = line.split(":")[1].strip()
            elif "Cluster:" in line:
                cluster = line.split(":")[1].strip()
            elif "User/Group:" in line:
                user_group = line.split(":")[1].strip()
            elif "State:" in line:
                state = line.split(":")[1].strip()
            elif "Nodes:" in line:
                nodes = line.split(":")[1].strip()
            elif "Cores per node:" in line:
                cores_per_node = line.split(":")[1].strip()
            elif "CPU Utilized:" in line:
                cpu_utilized = line.split(":")[1].strip()
            elif "CPU Efficiency:" in line:
                cpu_efficiency = ":".join(line.split(":")[1:]).strip()
            elif "Job Wall-clock time:" in line:
                job_wall_clock_time = line.split(":")[1].strip()
            elif "Memory Utilized:" in line:
                memory_utilized = line.split(":")[1].strip()
            elif "Memory Efficiency:" in line:
                memory_efficiency = line.split(":")[1].strip()

        # Return a Job object
        return JobEff(job_id, cluster, user_group, state, nodes, cores_per_node,
                      cpu_utilized, cpu_efficiency, job_wall_clock_time, memory_utilized, memory_efficiency)

    def sacct(self, arguments_list):
        """
        Execute sacct command and parse output
        """
        arguments = ' '.join(arguments_list)
        command = f'sacct {arguments}'
        output = self.execute_command(command)
        filename = 'sacct_output.csv'
        df = self.read_output_to_dataframe(output, self.command_params['sacct'], filename)
        return df

class JobEff:
    def __init__(self, job_id, cluster, user_group, state, nodes, cores_per_node,
                 cpu_utilized, cpu_efficiency, job_wall_clock_time, memory_utilized, memory_efficiency):
        self.job_id = job_id
        self.cluster = cluster
        self.user_group = user_group
        self.state = state
        self.nodes = nodes
        self.cores_per_node = cores_per_node
        self.cpu_utilized = cpu_utilized
        self.cpu_efficiency = cpu_efficiency
        self.job_wall_clock_time = job_wall_clock_time
        self.memory_utilized = memory_utilized
        self.memory_efficiency = memory_efficiency
        self.command_args = ["--allusers"]  # can be set by user when called

    def __str__(self):
        return (
            f"Job ID: {self.job_id}\n"
            f"Cluster: {self.cluster}\n"
            f"User/Group: {self.user_group}\n"
            f"State: {self.state}\n"
            f"Nodes: {self.nodes}\n"
            f"Cores per node: {self.cores_per_node}\n"
            f"CPU Utilized: {self.cpu_utilized}\n"
            f"CPU Efficiency: {self.cpu_efficiency}\n"
            f"Job Wall-clock time: {self.job_wall_clock_time}\n"
            f"Memory Utilized: {self.memory_utilized}\n"
            f"Memory Efficiency: {self.memory_efficiency}\n"
        )


class SeffWrapper:
    def __init__(self):
        pass

    @staticmethod
    def parse_time(time_str):
        # print(f"time_str:{time_str}")
        days, hours, minutes, seconds = 0, 0, 0, 0
        if '-' in time_str:  # Check for days in the string
            days_str, time_str = time_str.split('-')
            days = int(days_str)
        time_parts = time_str.split(':')
        if len(time_parts) == 3:
            hours, minutes, seconds = map(int, time_parts)
        elif len(time_parts) == 2:
            hours, minutes = map(int, time_parts)
        elif len(time_parts) == 1:
            hours = int(time_parts[0])
        else:
            raise ValueError(f"Unexpected time format: {time_str}")

        total_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds
        return total_seconds

    def fetch_efficiency(self, job_id, job_status=None):
        command = ["seff", str(job_id)]
        seff_output = subprocess.check_output(command).decode("utf-8")

        lines = seff_output.split("\n")
        data = {}

        for line in lines:
            if "Job ID:" in line:
                data["Job ID"] = line.split(":")[1].strip()
            elif "Cluster:" in line:
                data["Cluster"] = line.split(":")[1].strip()
            elif "User/Group:" in line:
                data["User/Group"] = line.split(":")[1].strip()
            elif "State:" in line:
                data["State"] = line.split("State:")[1].strip().split(" (")[0]
            elif "Nodes:" in line:
                data["Nodes"] = int(line.split(":")[1].strip())
            elif "Cores per node:" in line:
                data["Cores per node"] = int(line.split(":")[1].strip())
            elif "CPU Utilized:" in line:
                time_data = line.split("CPU Utilized:")[1].strip()
                data["CPU Utilized"] = self.parse_time(time_data)
            elif "CPU Efficiency:" in line:
                data["CPU Efficiency"] = line.split(":")[1].strip().split()[0]
            elif "Job Wall-clock time:" in line:
                time_data = line.split("Job Wall-clock time:")[1].strip()
                data["Job Wall-clock time"] = self.parse_time(time_data)
            elif "Memory Utilized:" in line:
                data["Memory Utilized"] = line.split(":")[1].strip()
            elif "Memory Efficiency:" in line:
                data["Memory Efficiency"] = line.split(":")[1].strip().split()[0]

        # If a specific job_status is specified, only return data if the job matches the status
        if job_status:
            if data.get("State") == job_status:
                self.print_job_info(data)
                return data
            else:
                return None
        else:
            self.print_job_info(data)
            return data

    def print_job_info(self, data):
        for key, value in data.items():
            print(f"{key}: {value}")
        print("\n-----------------------\n")

class SacctTools:
    def __init__(self, verbose=False, separator="\s+", col_names_line_num=0, first_data_row_num=2, exclude_keywords=["batch", "extern"]):
        self.verbose = verbose
        self.exclude_keywords = exclude_keywords
        self.separator = separator
        self.col_names_line_num = col_names_line_num
        self.first_data_row_num = first_data_row_num

    def sacct(self):
        command = ["sacct"] + self.command_args
        print(f"Running command: {command}")
        sacct_output = subprocess.check_output(command).decode("utf-8")
        return sacct_output

    def parse_output_to_df(self, sacct_output):  # TODO: needs some error handling ex. when output is empty
        # Split output into lines
        lines = sacct_output.strip().split("\n")

        # get column names
        columns = lines[self.col_names_line_num].split()

        # Split remaining lines into rows
        rows = [line.split() for line in lines[self.first_data_row_num:]]

        # Create DataFrame
        df = pd.DataFrame(rows, columns=columns)

        return df

    def write_output_to_csv(self, df, file_name):
        df.to_csv(OUTPUT_DIR + file_name, index=False)

    def read_output_to_dataframe(self, csv_file_name):
        sacct_output = self.sacct()
        df = self.parse_output_to_df(sacct_output)

        # Drop rows where 'JobName' contains any string from self.exclude_keywords
        for keyword in self.exclude_keywords:
            df = df[~df['JobName'].str.contains(keyword)]

        if self.verbose:
            self.write_output_to_csv(df, csv_file_name)

        return df

    def get_data(self, csv_file_name=None, command_args=["--allusers"]):
        self.command_args = command_args
        if csv_file_name is None:
            # Construct file name from command arguments
            csv_file_name = "sacct_" + "_".join(self.command_args).replace("-", "") + "_" + time.strftime("%Y%m%d%H%M%S") + ".csv"

        return self.read_output_to_dataframe(csv_file_name)


class SReport:
    def __init__(self, verbose=False, row_with_column_names=4, out_dir="untitled"):
        self.verbose = verbose
        self.report_data = ""
        self.output_dir = out_dir
        self.row_with_column_names = row_with_column_names
        self.default_options = ['-t', 'hours', '-T', 'billing']
        # create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)


    def _run_command(self, command):
        if self.verbose:
            print(" ".join(command))
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stdout, stderr

    def _generate_report(self, report_type, report, options=None):
        # command = ['sreport'] + [report_type, report]
        command = ['sreport'] + self.default_options + [report_type, report]
        if options:
            command.extend(options)
        stdout, stderr = self._run_command(command)
        # Skip lines until the data starts
        stdout_decoded = stdout.decode()
        # print(stdout_decoded)

        lines = stdout_decoded.split('\n')
        # for i, line in enumerate(lines):
        #     if line.startswith('Cluster|Account'):
        #         start_index = i
        #         break

        self.report_data = "\n".join(lines[self.row_with_column_names:])

        if self.verbose:
            self.output_filename = f"{time.strftime('%Y%m%d%H%M%S')}.csv".replace("-", "").replace("/", "_")

    def write_output_to_csv(self, df):
        if self.verbose:
            print(f"DEBUG: output_dir={self.output_dir}, output_filename={self.output_filename}")
        df.to_csv("/".join([self.output_dir, self.output_filename]), index=False)

    def cluster_report(self, report, options=None):
        options.append('Format=' + CLUSTER_FORMAT)
        self._generate_report('cluster', report, options)

    def job_report(self, report, options=None):
        self._generate_report('job', report, options)

    def reservation_report(self, report, options=None):
        self._generate_report('reservation', report, options)

    def user_report(self, report, options=None):
        self._generate_report('user', report, options)

    def get_report_data(self, exclude_accounts=False, exclude_users=False, only_csu_general_and_projects=False, only_institutions=False):
        lines = self.report_data.split("\n")[2:]  # Ignore the first two lines.
        data = []
        for line in lines:
            parts = line.split()
            if not parts:  # Skip empty lines
                continue
            cluster = parts.pop(0)  # The first element is always 'Cluster'
            account = parts.pop(0)  # The second element is always 'Account'
            # Check if we have 'Login' and 'Proper Name'
            if not parts[0].isdigit():
                login = parts.pop(0)
                # 'Proper Name' is everything up to the last two elements ('Used' and 'Energy')
                proper_name = " ".join(parts[:-2])
                used, energy = parts[-2:]
            else:  # 'Login' and 'Proper Name' are empty
                login = ''
                proper_name = ''
                used, energy = parts
            data.append([cluster, account, login, proper_name, used, energy])
        df = pd.DataFrame(data, columns=["Cluster", "Account", "Login", "Proper Name", "Used", "Energy"])
        # df = pd.DataFrame(data, columns=["Cluster", "Account", "Login", "Proper Name", "TRES Name", "Used"])
        df.columns = df.columns.str.strip()  # Strip extra spaces from column names
        if self.verbose:
            self.write_output_to_csv(df)

        try:
            df['Used'] = df['Used'].astype(float)  # Convert 'Used' column to float
        except Exception as e:
            print(f"Error converting 'Used' column to float: {str(e)}")
        
        if only_csu_general_and_projects:
            # only keep rows where Account is csu-general or csu-projects and login is empty
            df = df[(df['Account'].str.contains('csu-general')) | (df['Account'].str.contains('csu-projects'))]
        if only_institutions:
            # only keep rows where Account is csu, ucb, or rmacc and login is empty
            df = df[(df['Account'] == 'csu') | (df['Account'] == 'ucb') | (df['Account'] == 'rmacc')]
        if exclude_users:
            # remove data where Login is not empty
            df = df[df['Login'] == '']
        if exclude_accounts:
            # remove data where Login is empty
            df = df[df['Login'] != '']
        if self.verbose:
            print(df.head())
        return df
