import re

# مسیر فایل‌های ورودی و خروجی
input_file = r'D:\AVIDA\CODE\Invoice\Dep_in.txt'
output_file = r'D:\AVIDA\CODE\Invoice\Dep_out.txt'

# خواندن محتوای فایل ورودی
with open(input_file, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# استخراج مبالغ واریزها و تاریخ‌ها
deposit_amounts = []
deposit_lines = []
pattern = r'(\d+)\s+هزار تومان\s+-\s+در تاریخ\s+([\d\-]+)'

for line in lines:
    match = re.search(pattern, line)
    if match:
        amount = int(match.group(1))
        date = match.group(2)
        deposit_amounts.append(amount)
        deposit_lines.append(line.strip())

# محاسبه جمع واریزها
total_deposits = sum(deposit_amounts)

# دریافت مبلغ مانده از قبل از کاربر
previous_balance = int(input('Mande Ghabli: '))

# دریافت شماره روز ماه از کاربر
day_of_month = input('Adade Ruz (01-31) : ')

# محاسبه جمع کل مانده حساب
total_balance = previous_balance - total_deposits

# ساختن محتوای خروجی
output_lines = []

output_lines.append('💳 واریز ها :\n')
output_lines.append('\n')

for line in deposit_lines:
    output_lines.append(line + '\n')

output_lines.append('____________________________________\n')
output_lines.append(f'جمع واریز ها:  {total_deposits}\n')
output_lines.append(f'مبلغ مانده از قبل:  {previous_balance}\n')
output_lines.append('\n')
output_lines.append(f'در تاریخ:  1403/12/{day_of_month}\n')
output_lines.append(f'جمع کل مانده حساب شما:  {total_balance} هزار تومان\n')
output_lines.append('.\n')

# نوشتن محتوای جدید در فایل خروجی
with open(output_file, 'w', encoding='utf-8') as file:
    file.writelines(output_lines)
