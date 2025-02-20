import re
from datetime import datetime
from persiantools.jdatetime import JalaliDate

def process_text(line):
    if not any(keyword in line for keyword in ["تمدید شد ✅", "تمدید شد✅", "تمدید شد  ✅", "🟢"]):
        return None 

    line = re.sub(r"\s+", " ", line).strip()

    GIG = "(گیگ|گیک|کیگ|گبگ|کیک)"
    SAD = r"صد[ .]?و?[ .]?"
    SHST = "(شصت|شصد)"
    SHST_R = "(شصت روز|شصد روز)"
    NVD_R = "نود روز"
    BIST = "بیست"

    mappings = [
        (rf"{SAD}پنجاه {GIG}", "✅  [195]"), # 150G
        (rf"{SAD}{BIST} {GIG}.*?({SAD}{BIST} روز)", "✅  [180]"), # 120G  120R
        (rf"{SAD}{BIST} {GIG}.*?{NVD_R}", "✅  [165]"), # 120G  90R
        (rf"{SAD}{BIST} {GIG}", "✅  [156]"), # 120G   30R 60R
        (rf"\bصد {GIG}\b.*?{NVD_R}", "✅  [150]"), # 100G  90R
        (rf"\bصد {GIG}\b", "✅  [130]"), # 100G  30R 60R
        (rf"نود {GIG}.*?{NVD_R}", "✅  [135]"), # 90G  90R
        (rf"نود {GIG}.*?({SHST_R})", "✅  [125]"), # 90G  60R
        (rf"نود {GIG}", "✅  [117]"), # 90G
        (rf"هشتاد {GIG}(?!.*{SAD}هشتاد {GIG}).*?({SHST_R})", "✅  [110]"), # 80G  60R
        (rf"هشتاد {GIG}(?!.*{SAD}هشتاد {GIG})", "✅  [104]"), # 80G
        (rf"هفتاد {GIG}", "✅  [91]"), # 70G
        (rf"{SHST} {GIG}(?!.*{SAD}{SHST} {GIG}).*?{NVD_R}", "✅  [105]"), # 60G  90R
        (rf"{SHST} {GIG}(?!.*{SAD}{SHST} {GIG}).*?({SHST_R})", "✅  [90]"), # 60G  60R
        (rf"{SHST} {GIG}(?!.*{SAD}{SHST} {GIG})", "✅  [78]"), # 60G
        (rf"پنجاه {GIG}(?!.*{SAD}پنجاه {GIG})", "✅  [65]"), # 50G
        (rf"چهل {GIG}(?!.*{SAD}چهل {GIG}).*?({SHST_R})", "✅  [70]"), # 40G  60R
        (rf"چهل {GIG}(?!.*{SAD}چهل {GIG})", "✅  [55]"), # 40G
        (rf"سی {GIG}", "✅  [45]"), # 30G
        (rf"{BIST} {GIG}(?!.*{SAD}{BIST} {GIG})", "✅  [35]"), # 20G
        (rf"ده {GIG}", "✅  [25]") # 10G
        ]

    matched = False 

    for pattern, replacement in mappings:
        if re.search(pattern, line):
            line = re.sub(r"✅", replacement, line)
            matched = True
            break 

    #  قیمت دلخواه برای تمدید شد ✅
    if not matched and re.fullmatch(r"[\S ]+ تمدید شد ?✅", line):
        line = re.sub(r"✅", "✅  [6666]", line)
        matched = True

    #  قیمت کانفیگ جدید 🟢
    if "🟢" in line:
        line = line.replace("🟢", "  [7777]  🟢")

    #  خطوط نامفهوم
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
            file.write(f"فاصله زمانی: {date_diff} روز\n\n")

def calculate_sum_from_output(output_path, MANDEH, RUZ):
    with open(output_path, "r", encoding="utf-8") as file:
        content = file.read()

    numbers = [int(num) for num in re.findall(r"\[(\d+)\]", content)]
    total_sum = sum(numbers)

    with open(output_path, "a", encoding="utf-8") as file:
        file.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        file.write("📝\n")
        file.write(f"مبلغ این فاکتور: `{total_sum}`\n")
        file.write("-----------------------------\n")
        file.write(f"مبلغ مانده از قبل: `{MANDEH}`\n")
        file.write("-----------------------------\n")
#        file.write("📝\n")
        file.write(f"در تاریخ:  1403/12/{RUZ}\n")
        file.write(f"جمع کل مانده حساب شما:  `{int(MANDEH) + total_sum}` هزار تومان")

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

    checkmark_phrases = ["تمدید شد ✅", "تمدید شد✅", "تمدید شد  ✅"]

    for line in lines:
        total_checkmarks += sum(line.count(phrase) for phrase in checkmark_phrases)
        total_green_marks += line.count("🟢")

        processed_line = process_text(line)
        if processed_line:
            processed_lines.append(processed_line)
            if "[000000]" in processed_line:
                review_lines.append(processed_line)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(" 🧮  صورتحساب شما:\n")
        file.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")
#        file.write("📝\n")
        file.writelines(processed_lines)
        file.write("\n")
        file.write("--------------\n")
        file.write(f"تعداد تمدیدی ها ✅:  {total_checkmarks} عدد \n")
        file.write(f"تعداد خرید های جدید 🟢:  {total_green_marks} عدد \n")
        file.write(f"تعداد کل سفارشات:  {total_checkmarks + total_green_marks} عدد \n")

    with open(editme_path, "w", encoding="utf-8") as file:
        file.writelines(review_lines)
        file.write(f"\nتعداد کل 🟢: {total_green_marks} عدد\n")

    extract_dates(input_path, history_path, output_path)

    MANDEH = input("Mandeh Ghabli:")
    RUZ = input("َAdade Emruz:")
    calculate_sum_from_output(output_path, MANDEH, RUZ)

if __name__ == "__main__":
    main()