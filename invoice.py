import re
from datetime import datetime
from persiantools.jdatetime import JalaliDate

def process_text(line):
    if not any(keyword in line for keyword in ["تمدید شد ✅", "تمدید شد✅", "تمدید شد  ✅", "🟢"]):
        return None  # در این حالت خط حذف می‌شود

    # حذف فاصله‌های اضافی و نرمال‌سازی متن
    line = re.sub(r"\s+", " ", line).strip()

    mappings = [
        (r"صد.?و?.?پنجاه (گیگ|گیک|کیگ|کیک)", "✅  [195]"),
        (r"صد.?و?.?بیست (گیگ|گیک|کیگ|کیک).*?(صد.?و?.?بیست روز)", "✅  [180]"),
        (r"صد.?و?.?بیست (گیگ|گیک|کیگ|کیک).*?نود روز", "✅  [165]"),
        (r"صد.?و?.?بیست (گیگ|گیک|کیگ|کیک)", "✅  [156]"),
        (r"\bصد (گیگ|گیک|کیگ|کیک)\b.*?نود روز", "✅  [150]"),
        (r"\bصد (گیگ|گیک|کیگ|کیک)\b", "✅  [130]"),
        (r"نود (گیگ|گیک|کیگ|کیک).*?نود روز", "✅  [135]"),
        (r"نود (گیگ|گیک|کیگ|کیک).*?(شصت روز|شصد روز)", "✅  [120]"),
        (r"نود (گیگ|گیک|کیگ|کیک)", "✅  [117]"),
        (r"هشتاد (گیگ|گیک|کیگ|کیک)(?!.*صد.?و?.?هشتاد (گیگ|گیک|کیگ|کیک)).*?(شصت روز|شصد روز)", "✅  [110]"),
        (r"هشتاد (گیگ|گیک|کیگ|کیک)(?!.*صد.?و?.?هشتاد (گیگ|گیک|کیگ|کیک))", "✅  [104]"),
        (r"هفتاد (گیگ|گیک|کیگ|کیک)", "✅  [91]"),
        (r"(شصت|شصد) (گیگ|گیک|کیگ|کیک)(?!.*صد.?و?.?شصت (گیگ|گیک|کیگ|کیک)).*?نود روز", "✅  [105]"),
        (r"(شصت|شصد) (گیگ|گیک|کیگ|کیک)(?!.*صد.?و?.?شصت (گیگ|گیک|کیگ|کیک)).*?(شصت روز|شصد روز)", "✅  [90]"),
        (r"(شصت|شصد) (گیگ|گیک|کیگ|کیک)(?!.*صد.?و?.?شصت (گیگ|گیک|کیگ|کیک))", "✅  [78]"),
        (r"پنجاه (گیگ|گیک|کیگ|کیک)(?!.*صد.?و?.?پنجاه (گیگ|گیک|کیگ|کیک))", "✅  [65]"),
        (r"چهل (گیگ|گیک|کیگ|کیک)(?!.*صد.?و?.?چهل (گیگ|گیک|کیگ|کیک)).*?(شصت روز|شصد روز)", "✅  [70]"),
        (r"چهل (گیگ|گیک|کیگ|کیک)(?!.*صد.?و?.?چهل (گیگ|گیک|کیگ|کیک))", "✅  [55]"),
        (r"سی (گیگ|گیک|کیگ|کیک)", "✅  [45]"),
        (r"بیست (گیگ|گیک|کیگ|کیک)(?!.*صد.?و?.?بیست (گیگ|گیک|کیگ|کیک))", "✅  [35]"),
        (r"ده (گیگ|گیک|کیگ|کیک)", "✅  [25]")
    ]

    matched = False  # متغیر برای بررسی اینکه آیا جایگزینی انجام شده است یا نه

    for pattern, replacement in mappings:
        if re.search(pattern, line):
            line = re.sub(r"✅", replacement, line)
            matched = True
            break  # پس از اولین جایگزینی موفق، حلقه متوقف شود

    # تغییر مقدار `line` پس از جایگزینی 🟢
    if "🟢" in line:
        line = line.replace("🟢", "🟢  [000000]")

    # اگر هیچ جایگزینی انجام نشد، "✅" را به "✅  [000000]" تغییر بده
    if not matched:
        line = re.sub(r"✅", "✅  [000000]", line)

    return line + "\n"  # افزودن کاراکتر newline در انتهای هر خط خروجی

def extract_dates(input_path, history_path, output_path):
    with open(input_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    dates = re.findall(r"\[(\d{2})-([A-Za-z]{3})-(\d{2}) (\d{2}:\d{2})\]", "".join(lines))
    
    month_map = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
                 "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
    
    converted_dates = []
    miladi_dates = []
    for day, month, year, time in dates:
        year_full = int("20" + year)
        month_num = month_map[month]
        day = int(day)
        
        miladi_date = datetime(year_full, int(month_num), day)
        shamsi_date = JalaliDate(miladi_date).strftime("%Y/%m/%d")
        miladi_dates.append(miladi_date)
        
        converted_dates.append(f"--------------------------------\n{day} {month} {year_full}\n{day}-{month_num}-{year_full} {time}\n{shamsi_date}\n--------------------------------\n")
    
    with open(history_path, "w", encoding="utf-8") as file:
        file.writelines(converted_dates)
    
    if miladi_dates:
        first_date = miladi_dates[0]
        last_date = miladi_dates[-1]
        date_diff = (last_date - first_date).days
        first_shamsi = JalaliDate(first_date).strftime("%Y/%m/%d")
        last_shamsi = JalaliDate(last_date).strftime("%Y/%m/%d")
        
        with open(output_path, "a", encoding="utf-8") as file:
            file.write("\n________________________________________\n")
            file.write("این گزارش از تاریخ:\n")
            file.write("----------------------\n")
            file.write(f"{first_date.strftime('%d %b %Y')}\n")
            file.write(f"{first_shamsi}\n")
            file.write("----------------------\n")
            file.write("تا تاریخ:\n")
            file.write("----------------------\n")
            file.write(f"{last_date.strftime('%d %b %Y')}\n")
            file.write(f"{last_shamsi}\n")
            file.write("----------------------\n")
            file.write(f"فاصله زمانی: {date_diff} روز\n")
            file.write("________________________________________\n")

def calculate_sum_from_output(output_path):
    with open(output_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    numbers = [int(num) for num in re.findall(r"\[(\d+)\]", content)]
    total_sum = sum(numbers)
    
    with open(output_path, "a", encoding="utf-8") as file:
        file.write("________________________________________\n")
        file.write(f"جمع کل: {total_sum} هزار تومان\n")

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
        file.write("\n\n")
        file.write("________________________________________\n")
        file.write("________________________________________\n")
        file.write("________________________________________\n")
        file.write(f"تعداد کل ✅: {total_checkmarks} عدد\n")
        file.write(f"تعداد کل 🟢: {total_green_marks} عدد\n")
        file.write("----------------------\n")
        file.write(f"تعداد کل رکوردها: {total_checkmarks + total_green_marks} عدد\n")
        file.write("________________________________________")
    
    with open(editme_path, "w", encoding="utf-8") as file:
        file.writelines(review_lines)
        file.write(f"\nتعداد کل 🟢: {total_green_marks} عدد\n")
    
    extract_dates(input_path, history_path, output_path)
    calculate_sum_from_output(output_path)

if __name__ == "__main__":
    main()
