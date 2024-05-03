from flask import Flask, render_template, request
import pandas as pd
import threading
import os

app = Flask(__name__)

class FileProcessor:
    def __init__(self, file_path):
        """
        Initializes a new instance of the `FileProcessor` class.

        Args:
            file_path (str): The path to the file to be processed.

        Initializes the following instance variables:
            - file_path (str): The path to the file to be processed.
            - file_size (int): The size of the file in gigabytes.
            - num_columns (int): The number of columns in the file.
            - column_lengths (List[int]): The maximum length of each column in the file.
            - num_rows (int): The number of rows in the file.
            - col_descriptions (pandas.DataFrame): The description of each column in the file.
            - column_types (List[type]): The data type of each column in the file.
            - column_categories (List[str]): The category of each column in the file.
        """
        self.file_path = file_path
        self.file_size = 0
        self.num_columns = 0
        self.column_lengths = []
        self.num_rows = 0
        self.col_descriptions = None
        self.column_types = []  # Initialize column_types here
        self.column_categories = []  # Initialize column_categories if not already done

    def process_file(self):
        # Read the file into a pandas dataframe
        df = pd.read_csv(self.file_path)

        # Calculate the file size in GB
        self.file_size = os.path.getsize(self.file_path) / (1024 * 1024 * 1024)

        # Get the number of columns
        self.num_columns = len(df.columns)

        # Get the length of each column
        for col in df.columns:
            self.column_lengths.append(max(df[col].astype(str).apply(len)))

        # Get the number of rows
        self.num_rows = len(df)

        self.col_descriptions = df.describe().apply(lambda s: s.apply('{0:.5f}'.format))

        # Get the data type of each column
        for col in df.columns:
            self.column_types.append(df[col].dtype)

        # Determine the category of each column
        for col in df.columns:
            if pd.to_numeric(df[col], errors='coerce').notnull().all():
                self.column_categories.append("numeric")
            elif pd.to_datetime(df[col], errors='coerce', format='%Y-%m-%d').notnull().all():
                self.column_categories.append("date")
            else:
                self.column_categories.append("alphanumeric")
    def print_results(self):
        print(f"File size: {self.file_size:.2f} GB")
        print(f"\nNumber of rows: {self.num_rows}")
        print(f"\nNumber of columns: {self.num_columns}")
        print("\nColumn(s) max width:")
        for i, length in enumerate(self.column_lengths):
            print(f"Column {i}: {length}")
        print(f"\nColumn(s) description: \n{self.col_descriptions}")
        print("\nColumn data types:")
        for i, dtype in enumerate(self.column_types):
            print(f"Column {i}: {dtype}")
        print("\nColumn categories:")
        for i, category in enumerate(self.column_categories):
            print(f"Column {i}: {category}")
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file_path' in request.form:
        file_path = request.form['file_path']
        processor = FileProcessor(file_path)
        processor.process_file()
        return render_template('results.html', file_size=processor.file_size,
                               num_columns=processor.num_columns,
                               column_lengths=processor.column_lengths,
                               column_types=processor.column_types,
                               column_categories=processor.column_categories,
                               num_rows=processor.num_rows)
    else:
        return "File path not provided"
if __name__ == '__main__':
    app.run(debug=True)
