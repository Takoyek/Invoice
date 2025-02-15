import re
from datetime import datetime
from persiantools.jdatetime import JalaliDate

def process_text(line):
    if not any(keyword in line for keyword in ["تمدید شد ✅", "تمدید شد✅", "🟢"]):
        return None

    if "ده گیگ" in line:
        return re.sub(r"✅", "✅  [25]", line)

    if "بیست گیگ" in line and not any(phrase in line for phrase in ["صد و بیست گیگ", "صدوبیست گیگ"]):
        return re.sub(r"✅", "✅  [35]", line)

    if "🟢" in line:
        return line.replace("🟢", "🟢  [000000]")

    return line

def extract_dates(input_path, history_path):
    with open(input_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    dates = re.findall(r"\[(\d{2})-([A-Za-z]{3})-(\d{2}) (\d{2}:\d{2})\]", "".join(lines))
    
    month_map = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
                 "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
    
    converted_dates = []
    for day, month, year, time in dates:
        year_full = int("20" + year)  # تبدیل سال دو رقمی به چهار رقمی
        month_num = month_map[month]
        day = int(day)
        
        miladi_date = datetime(year_full, int(month_num), day)
        shamsi_date = JalaliDate(miladi_date).strftime("%Y/%m/%d")
        
        converted_dates.append(f"--------------------------------\n{day} {month} {year_full}\n{day}-{month_num}-{year_full} {time}\n{shamsi_date}\n--------------------------------\n")
    
    with open(history_path, "w", encoding="utf-8") as file:
        file.writelines(converted_dates)

def calculate_sum_from_output(output_path):
    with open(output_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    numbers = [int(num) for num in re.findall(r"\[(\d+)\]", content)]
    total_sum = sum(numbers)
    
    with open(output_path, "a", encoding="utf-8") as file:
        file.write(f"\nجمع کل: {total_sum} تومان\n")

def main():
    input_path = "D:\\AVIDA\\CODE\\Invoice\\Input.txt"
    output_path = "D:\\AVIDA\\CODE\\Invoice\\Output.txt"
    editme_path = "D:\\AVIDA\\CODE\\Invoice\\EditMe.txt"
    history_path = "D:\\AVIDA\\CODE\\Invoice\\History.txt"

    processed_lines = []
    review_lines = []

    total_checkmarks = 0
    total_green_marks = 0
    
    with open(input_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        total_checkmarks += line.count("✅")
        total_green_marks += line.count("🟢")
        
        processed_line = process_text(line)
        if processed_line:
            processed_lines.append(processed_line)
            if "[000000]" in processed_line:
                review_lines.append(processed_line)

    with open(output_path, "w", encoding="utf-8") as file:
        file.writelines(processed_lines)
        file.write(f"\nتعداد کل ✅: {total_checkmarks} عدد\n")
        file.write(f"\nتعداد کل 🟢: {total_green_marks} عدد\n")
        file.write(f"\nتعداد کل رکوردها: {total_checkmarks + total_green_marks} عدد\n")
    
    with open(editme_path, "w", encoding="utf-8") as file:
        file.writelines(review_lines)
        file.write(f"\nتعداد کل 🟢: {total_green_marks} عدد\n")
    
    # محاسبه و افزودن جمع کل اعداد داخل []
    calculate_sum_from_output(output_path)
    
    # استخراج تاریخ‌ها، تبدیل و ذخیره در فایل History.txt
    extract_dates(input_path, history_path)

if __name__ == "__main__":
    main()
