import re
from datetime import datetime
from persiantools.jdatetime import JalaliDate

def process_text(line):
    if not any(keyword in line for keyword in ["تمدید شد ✅", "تمدید شد✅", "تمدید شد  ✅", "🟢"]):
        return None 

    line = re.sub(r"\s+", " ", line).strip()

    GIGABYTE = "(گیگ|گیک|کیگ|گبگ|کیک)"
    mappings = [
        (rf"صد[ .]?و?[ .]?پنجاه {GIGABYTE}", "✅  [195]"),
        (rf"صد[ .]?و?[ .]?بیست {GIGABYTE}.*?(صد[ .]?و?[ .]?بیست روز)", "✅  [180]"),
        (rf"صد[ .]?و?[ .]?بیست {GIGABYTE}.*?نود روز", "✅  [165]"),
        (rf"صد[ .]?و?[ .]?بیست {GIGABYTE}", "✅  [156]"),
        (rf"\bصد {GIGABYTE}\b.*?نود روز", "✅  [150]"),
        (rf"\bصد {GIGABYTE}\b", "✅  [170]"),
        (rf"نود {GIGABYTE}.*?نود روز", "✅  [135]"),
        (rf"نود {GIGABYTE}.*?(شصت روز|شصد روز)", "✅  [120]"),
        (rf"نود {GIGABYTE}", "✅  [117]"),
        (rf"هشتاد {GIGABYTE}(?!.*صد[ .]?و?[ .]?هشتاد {GIGABYTE}).*?(شصت روز|شصد روز)", "✅  [110]"),
        (rf"هشتاد {GIGABYTE}(?!.*صد[ .]?و?[ .]?هشتاد {GIGABYTE})", "✅  [104]"),
        (rf"هفتاد {GIGABYTE}", "✅  [91]"),
        (rf"(شصت|شصد) {GIGABYTE}(?!.*صد[ .]?و?[ .]?(شصت|شصد) {GIGABYTE}).*?نود روز", "✅  [105]"),
        (rf"(شصت|شصد) {GIGABYTE}(?!.*صد[ .]?و?[ .]?(شصت|شصد) {GIGABYTE}).*?(شصت روز|شصد روز)", "✅  [90]"),
        (rf"(شصت|شصد) {GIGABYTE}(?!.*صد[ .]?و?[ .]?(شصت|شصد) {GIGABYTE})", "✅  [78]"),
        (rf"پنجاه {GIGABYTE}(?!.*صد[ .]?و?[ .]?پنجاه {GIGABYTE})", "✅  [85]"),
        (rf"چهل {GIGABYTE}(?!.*صد[ .]?و?[ .]?چهل {GIGABYTE}).*?(شصت روز|شصد روز)", "✅  [70]"),
        (rf"چهل {GIGABYTE}(?!.*صد[ .]?و?[ .]?چهل {GIGABYTE})", "✅  [55]"),
        (rf"سی {GIGABYTE}", "✅  [65]"),
        (rf"بیست {GIGABYTE}(?!.*صد[ .]?و?[ .]?بیست {GIGABYTE})", "✅  [35]"),
        (rf"ده {GIGABYTE}", "✅  [25]")
    ]

    matched = False 

    for pattern, replacement in mappings:
        if re.search(pattern, line):
            line = re.sub(r"✅", replacement, line)
            matched = True
            break 

    if "🟢" in line:
        line = line.replace("🟢", "🟢  [000000]")

    # اگر هیچ جایگزینی انجام نشد
    if not matched:
        line = re.sub(r"✅", "✅  [000000]", line)

    return line + "\n" 


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
            file.write("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
            file.write("📅\n")
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

def calculate_sum_from_output(output_path):
    with open(output_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    numbers = [int(num) for num in re.findall(r"\[(\d+)\]", content)]
    total_sum = sum(numbers)
    
    with open(output_path, "a", encoding="utf-8") as file:
        file.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        file.write("💰\n")
        file.write(f"مبلغ این فاکتور: `{total_sum}`\n")
        file.write("-----------------------------\n")
        file.write("مانده حساب قبلی: `000`\n\n")
        file.write("جمع مانده حساب تا تاریخ 1403/00/00\n")
        file.write("مبلغ:  `000` هزار تومان")

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

    checkmark_phrases = ["تمدید شد ✅", "تمدید شد✅", "تمدید شد  ✅"]

    for line in lines:
        total_checkmarks += sum(line.count(phrase) for phrase in checkmark_phrases)
        total_green_marks += line.count("🟢")


        
        processed_line = process_text(line)
        if processed_line:
            processed_lines.append(processed_line)
            if "[000000]" in processed_line:
                review_lines.append(processed_line)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write("🧮 خلاصه فاکتور شما:\n")  # اضافه کردن متن در ابتدای فایل
        file.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        file.write("🔍\n")
        file.writelines(processed_lines)
        file.write("\n")
        file.write("--------------\n")
        file.write(f"تعداد تمدیدها ✅: {total_checkmarks} عدد\n")
        file.write(f"تعداد خرید های جدید 🟢: {total_green_marks} عدد\n")
        file.write(f"تعداد کل رکوردها: {total_checkmarks + total_green_marks} عدد\n")
    
    with open(editme_path, "w", encoding="utf-8") as file:
        file.writelines(review_lines)
        file.write(f"\nتعداد کل 🟢: {total_green_marks} عدد\n")
    
    extract_dates(input_path, history_path, output_path)
    calculate_sum_from_output(output_path)

if __name__ == "__main__":
    main()
