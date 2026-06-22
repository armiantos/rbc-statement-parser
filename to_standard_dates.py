from datetime import datetime
import csv
import argparse

def find_date_column_index(headers: list[str], date_column_name: str) -> int:
    for i in range(len(headers)):
        if headers[i] == date_column_name:
            return i
    return -1 

def replace_csv_date(path_to_file: str, date_column_name: str):
    with open(path_to_file, mode='r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader) # Skip header row
        date_column = find_date_column_index(header, date_column_name)
        if (date_column == -1):
            raise Exception(f"Could not find column '{date_column_name}' in headers: {','.join(header)}")

        print(','.join(header))
        for row in reader:
            print(','.join([val if i != date_column else datetime.strptime(val, '%d %b %Y').isoformat() for (i, val) in enumerate(row)]))

def main():
    parser = argparse.ArgumentParser(description='Updates given csv file to standard yyyy-MM-dd format')
    parser.add_argument('path_to_file', type=str, help = 'Path to csv')
    parser.add_argument('date_column_name', type=str, help = 'Column name to update')

    args = parser.parse_args()
    replace_csv_date(args.path_to_file, args.date_column_name)

if __name__ == '__main__':
    main()
