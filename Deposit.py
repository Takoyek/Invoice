import re
import datetime
import os

def read_input_file(input_file):
    if not os.path.exists(input_file):
        print('Input file not found. Please check the file path.')
        exit()
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        return lines
    except IOError:
        print('Error reading the input file.')
        exit()

def extract_deposits(lines):
    deposits = []
    pattern = r'(\d+)\s+هزار تومان\s+-\s+در تاریخ\s+([\d\-]+)'
    for line in lines:
        match = re.search(pattern, line)
        if match:
            amount = int(match.group(1))
            date_str = match.group(2)
            # Convert the date string to a datetime object for sorting
            try:
                date_parts = date_str.split('-')
                date_parts = [int(part) for part in date_parts]
                # Assuming the date format is day-month-year
                date = datetime.date(year=date_parts[2], month=date_parts[1], day=date_parts[0])
            except ValueError:
                print(f'Invalid date format in line: {line.strip()}')
                continue
            deposits.append({'amount': amount, 'date': date, 'line': line.strip()})
    # Sort deposits by date
    deposits.sort(key=lambda x: x['date'])
    deposit_amounts = [d['amount'] for d in deposits]
    deposit_lines = [d['line'] for d in deposits]
    return deposit_amounts, deposit_lines

def get_previous_balance():
    while True:
        try:
            previous_balance = int(input('Mandeh Ghabli: '))
            return previous_balance
        except ValueError:
            print('Please enter a valid integer.')

def get_day_of_month():
    while True:
        day_of_month = input('Adade Emruz (01-31) : ')
        if day_of_month.isdigit() and 1 <= int(day_of_month) <= 31:
            day_of_month = f'{int(day_of_month):02d}'
            return day_of_month
        else:
            print('Please enter a number between 01 and 31.')

def calculate_totals(previous_balance, total_deposits):
    total_balance = previous_balance - total_deposits
    return total_balance

def write_output_file(output_file, deposit_lines, total_deposits, previous_balance, total_balance, day_of_month):
    output_lines = []
    output_lines.append('💳 واریز ها :\n')
    output_lines.append('____________________________________\n\n')
    for line in deposit_lines:
        output_lines.append(line + '\n')
    output_lines.append('____________________________________\n')
    output_lines.append(f'جمع واریز ها:  `{total_deposits}`\n')
    output_lines.append(f'مبلغ مانده از قبل:  `{previous_balance}`\n\n')
    output_lines.append(f'در تاریخ:  1403/12/{day_of_month}\n')
    output_lines.append(f'جمع کل مانده حساب شما:  `{total_balance}` هزار تومان\n')
    output_lines.append('.\n')
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.writelines(output_lines)
        print('Output file has been saved successfully.')
    except IOError:
        print('Error writing the output file.')

def main():
    input_file = r'D:\AVIDA\CODE\Invoice\Dep_in.txt'
    output_file = r'D:\AVIDA\CODE\Invoice\Dep_out.txt'

    lines = read_input_file(input_file)
    deposit_amounts, deposit_lines = extract_deposits(lines)
    total_deposits = sum(deposit_amounts)
    previous_balance = get_previous_balance()
    day_of_month = get_day_of_month()

    total_balance = calculate_totals(previous_balance, total_deposits)
    write_output_file(output_file, deposit_lines, total_deposits, previous_balance, total_balance, day_of_month)

if __name__ == '__main__':
    main()
