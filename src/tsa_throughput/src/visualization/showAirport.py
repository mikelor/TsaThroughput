import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

def process_tsa_throughput(filepath):
    """
    Reads a CSV file, calculates daily throughput, and creates a line graph, one line per year.

    Args:
        filepath: The path to the CSV file.

    Returns:
        None. Displays the graph. Prints informative error messages.
    """
    try:
        # Set options to display all rows and columns
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 0) # Adjusts the output width to fit the content

        # Read the CSV file.
        df = pd.read_csv(filepath)

        # Convert 'Date' column to datetime objects. Handle potential errors.
        try:
            df['Date'] = pd.to_datetime(df['Date'])
        except Exception as e:
            print(f"Error converting 'Date' column to datetime: {e}")
            return

        # Calculate daily throughput (sum of all LAS terminals for each hour).
        try:
            numeric_cols = df.select_dtypes(include=['number']).columns  # Get numeric columns
            df['DailyThroughput'] = df[numeric_cols].sum(axis=1)  # Sum only numeric cols
        except KeyError as e:
            print(f"Error: One or more TSA throughput columns are missing from the CSV. Check for typos in column names: {e}")
            return

        # Extract the year and format the date as mm/dd
        df['Year'] = df['Date'].dt.year
        df['MonthDay'] = df['Date'].dt.strftime('%m/%d')

        # Pivot the DataFrame to have mm/dd as rows and Year as columns
        try:
          pivot_df = df.pivot_table(index='MonthDay', columns='Year', values='DailyThroughput')
        except Exception as e:
          print(f"Error pivoting the table: {e}")
          return

        # Prepare the data for a clustered bar chart
        x = pivot_df.index
        width = 1.0 / len(pivot_df.columns)  # Adjust bar width based on the number of years
        group_gap = 0.5 # Space between the grouped bars for each day

        # Create the figure and axes
        fig, ax = plt.subplots(figsize=(25, 7))

        # Plot the bars for each year
        num_groups = len(x) # Number of groups of bars (days)
        group_positions = np.arange(num_groups) # Integer positions for each group

        for i, year in enumerate(pivot_df.columns):
            offset = (width + group_gap) * (i - (len(pivot_df.columns) - 1) / 2)  # Calculate offset
            x_pos = group_positions + offset # Apply offset

            ax.bar(x_pos, pivot_df[year], width=width, label=str(year))

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_xlabel('Month/Day')
        ax.set_ylabel('Daily Throughput')
        ax.set_title('TSA Throughput per Day by Year (Clustered Bar Chart)')
        ax.set_xticks(group_positions) # Set x ticks
        ax.set_xticklabels(x, rotation=45, ha="right") # Set labels at those ticks
        ax.legend(title='Year')
        fig.tight_layout()  # Adjust layout to make room for rotated labels
        plt.grid(axis='y')  # Add a grid to the y-axis for readability
        
        plt.savefig(f'./Figure.Sample.png')
        plt.close(fig)
    

    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Replace 'TsaThroughput.Sample.csv' with your file path.
filepath = './data/processed/tsa/throughput/TsaThroughput.Sample.csv'
process_tsa_throughput(filepath)