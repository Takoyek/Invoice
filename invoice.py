import re
from datetime import datetime
from persiantools.jdatetime import JalaliDate

def process_text(line):
    # بررسی اگر خط شامل "تمدید شد ✅"، "تمدید شد✅"، "تمدید شد  ✅" یا "🟢" باشد
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
        (rf"{SAD}پنجاه {GIG}", "[240]"),  # 150G
        (rf"{SAD}{BIST} {GIG}.*?({SAD}{BIST} روز)", "[240]"),  # 120G 120R
        (rf"{SAD}{BIST} {GIG}.*?{NVD_R}", "[220]"),  # 120G 90R
        (rf"{SAD}{BIST} {GIG}", "[190]"),  # 120G 30R 60R
        (rf"\bصد {GIG}\b.*?{NVD_R}", "[190]"),  # 100G 90R
        (rf"\bصد {GIG}\b", "[160]"),  # 100G 30R 60R
        (rf"نود {GIG}.*?{NVD_R}", "[180]"),  # 90G 90R
        (rf"نود {GIG}.*?({SHST_R})", "[160]"),  # 90G 60R
        (rf"نود {GIG}", "[145]"),  # 90G
        (rf"هشتاد {GIG}(?!.*{SAD}هشتاد {GIG}).*?({SHST_R})", "[110]"),  # 80G 60R
        (rf"هشتاد {GIG}(?!.*{SAD}هشتاد {GIG})", "[130]"),  # 80G
        (rf"هفتاد {GIG}", "[115]"),  # 70G
        (rf"{SHST} {GIG}(?!.*{SAD}{SHST} {GIG}).*?{NVD_R}", "[135]"),  # 60G 90R
        (rf"{SHST} {GIG}(?!.*{SAD}{SHST} {GIG}).*?({SHST_R})", "[120]"),  # 60G 60R
        (rf"{SHST} {GIG}(?!.*{SAD}{SHST} {GIG})", "[100]"),  # 60G
        (rf"پنجاه {GIG}(?!.*{SAD}پنجاه {GIG})", "[85]"),  # 50G
        (rf"چهل {GIG}(?!.*{SAD}چهل {GIG}).*?({SHST_R})", "[90]"),  # 40G 60R
        (rf"چهل {GIG}(?!.*{SAD}چهل {GIG})", "[75]"),  # 40G
        (rf"سی {GIG}", "[60]"),  # 30G
        (rf"{BIST} {GIG}(?!.*{SAD}{BIST} {GIG})", "[45]"),  # 20G
        (rf"ده {GIG}", "[30]")  # 10G
    ]

    matched = False

    for pattern, replacement in mappings:
        if re.search(pattern, line):
            if "✅" in line:
                # جایگزینی "✅" با مقدار جایگزین
                line = line.replace("✅", f"✅  {replacement}")
            elif "🟢" in line:
                # افزودن مقدار جایگزین قبل از "🟢"
                line = line.replace("🟢", f"{replacement}  🟢")
            matched = True
            break

    # در صورتی که تطابقی پیدا نشد ولی خط شامل "✅" یا "🟢" بود
    if not matched and ("✅" in line or "🟢" in line):
        if "✅" in line:
            line = line.replace("✅", "✅  [000000]")
        elif "🟢" in line:
            line = line.replace("🟢", "[111111]  🟢")
        matched = True

    # اگر هنوز تطابقی پیدا نشده بود
    if not matched:
        if "✅" in line:
            line = line.replace("✅", "✅  [222222]")
        elif "🟢" in line:
            line = line.replace("🟢", "[333333]  🟢")

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
        
        converted_dates.append(
        f"__________________\n"
        f"{day} {month} {year_full}\n"
        f"{day}-{month_num}-{year_full} {time}\n"
        f"{shamsi_date}\n"
        f"__________________\n")

    with open(history_path, "w", encoding="utf-8") as file:
        file.writelines(converted_dates)
    
    if miladi_dates:
        first_date = miladi_dates[0]
        last_date = miladi_dates[-1]
        date_diff = (last_date - first_date).days
        first_shamsi = JalaliDate(first_date).strftime("%Y/%m/%d")
        last_shamsi = JalaliDate(last_date).strftime("%Y/%m/%d")
        
        with open(output_path, "a", encoding="utf-8") as file:
            file.write("____________________________________\n")
            file.write("📅\n")
            file.write("این گزارش از تاریخ:\n")
            file.write(f"{first_shamsi}\n")
            file.write(f"{first_date.strftime('%d %b %Y')}\n")
            file.write("تا تاریخ:\n")
            file.write(f"{last_shamsi}\n")
            file.write(f"{last_date.strftime('%d %b %Y')}\n")
            file.write(f"فاصله زمانی: {date_diff} روز\n")

def calculate_sum_from_output(output_path, MANDEH, current_date_str):
    with open(output_path, "r", encoding="utf-8") as file:
        content = file.read()

    numbers = [int(num) for num in re.findall(r"\[(\d+)\]", content)]
    total_sum = sum(numbers)

    with open(output_path, "a", encoding="utf-8") as file:
        file.write("____________________________________\n")
        file.write("📝\n")
        file.write(f"مبلغ این فاکتور: `{total_sum}`\n")
        file.write(f"مبلغ مانده از قبل: `{MANDEH}`\n\n")
        file.write(f"در تاریخ:  {current_date_str}\n")
        file.write(f"جمع کل مانده حساب شما:  `{int(MANDEH) + total_sum}` هزار تومان")
        file.write("\n.")

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
        file.write(" 🧮  صورتحساب شما:\n")
        file.write("____________________________________\n\n")
        file.writelines(processed_lines)
        file.write("____________________________________\n")
        file.write("📊\n")
        file.write(f"✅ تعداد تمدیدی ها:  {total_checkmarks} عدد \n")
        file.write(f"🟢 تعداد خرید های جدید:  {total_green_marks} عدد \n")
        file.write(f"تعداد کل سفارشات:  {total_checkmarks + total_green_marks} عدد \n")

    with open(editme_path, "w", encoding="utf-8") as file:
        file.writelines(review_lines)
        file.write(f"\nتعداد کل 🟢: {total_green_marks} عدد\n")

    extract_dates(input_path, history_path, output_path)

    # محاسبه تاریخ شمسی فعلی
    shamsi_today = JalaliDate.today()
    current_date_str = f"{shamsi_today.year}/{shamsi_today.month}/{shamsi_today.day}"

    MANDEH = input("Mandeh Ghabli: ")
    calculate_sum_from_output(output_path, MANDEH, current_date_str)

if __name__ == "__main__":
    main()