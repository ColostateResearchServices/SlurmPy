import pandas as pd
import subprocess
import time


class SacctTools:
    def __init__(self, verbose=False, separator = "\s+", col_names_line_num = 0, first_data_row_num = 2, command_args=["--allusers"], exclude_keywords=["batch", "extern"]):
        self.verbose = verbose
        self.command_args = command_args
        self.exclude_keywords = exclude_keywords
        self.separator = separator
        self.col_names_line_num = col_names_line_num
        self.first_data_row_num = first_data_row_num

    def sacct(self):
        command = ["sacct"] + self.command_args
        sacct_output = subprocess.check_output(command).decode("utf-8")
        return sacct_output

    def parse_output_to_df(self, sacct_output): #TODO: needs some error handling ex. when output is empty
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
        df.to_csv(file_name, index=False)

    def read_output_to_dataframe(self, csv_file_name):
        sacct_output = self.sacct()
        df = self.parse_output_to_df(sacct_output)

        # Drop rows where 'JobName' contains any string from self.exclude_keywords
        for keyword in self.exclude_keywords:
            df = df[~df['JobName'].str.contains(keyword)]

        if self.verbose:
            self.write_output_to_csv(df, csv_file_name)

        return df

    def get_data(self, csv_file_name=None):
        if csv_file_name is None:
            # Construct file name from command arguments
            csv_file_name = "sacct_" + "_".join(self.command_args).replace("-", "") + "_" + time.strftime("%Y%m%d%H%M%S") + ".csv"
        
        return self.read_output_to_dataframe(csv_file_name)
