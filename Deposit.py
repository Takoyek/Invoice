import re

# مسیر فایل‌های ورودی و خروجی
input_file = r'D:\AVIDA\CODE\Invoice\Dep_in.txt'
output_file = r'D:\AVIDA\CODE\Invoice\Dep_out.txt'

# خواندن محتوای فایل ورودی
with open(input_file, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# استخراج مبالغ واریزها
deposit_amounts = []
pattern = r'(\d+)\s+هزار تومان'
deposit_section = False

for line in lines:
    if '💳 واریز ها :' in line:
        deposit_section = True
        continue  # شروع بخش واریزها
    elif '____________________________________' in line:
        deposit_section = False  # پایان بخش واریزها
    if deposit_section:
        match = re.search(pattern, line)
        if match:
            amount = int(match.group(1))
            deposit_amounts.append(amount)

# محاسبه جمع واریزها
total_deposits = sum(deposit_amounts)

# دریافت مبلغ مانده از قبل از کاربر
previous_balance = int(input('Mande Ghabli: '))

# دریافت شماره روز ماه از کاربر
day_of_month = input('Adade Ruz (00-31) : ')

# محاسبه جمع کل مانده حساب
total_balance = previous_balance - total_deposits

# به‌روزرسانی خطوط فایل با مقادیر جدید
for i, line in enumerate(lines):
    if 'جمع واریز ها:' in line:
        lines[i] = f'جمع واریز ها:  {total_deposits}\n'
    elif 'مبلغ مانده از قبل:' in line:
        lines[i] = f'مبلغ مانده از قبل:  {previous_balance}\n'
    elif 'در تاریخ:' in line:
        lines[i] = f'در تاریخ:  1403/12/{day_of_month}\n'
    elif 'جمع کل مانده حساب شما:' in line:
        lines[i] = f'جمع کل مانده حساب شما:  {total_balance} هزار تومان\n'

# نوشتن محتوای جدید در فایل خروجی
with open(output_file, 'w', encoding='utf-8') as file:
    file.writelines(lines)
