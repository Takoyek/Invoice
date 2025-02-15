import re
from datetime import datetime
from persiantools.jdatetime import JalaliDate

def process_text(line):
    if not any(keyword in line for keyword in ["تمدید شد ✅", "تمدید شد✅", "🟢"]):
        return None

    if "ده گیگ" in line:
        return re.sub(r"✅", "✅  [25]", line)

    if "بیست گیگ" in line and not any(phrase in line for phrase in ["صد و بیست گیگ", "صدو بیست گیگ", "صدوبیست گیگ"]):
        return re.sub(r"✅", "✅  [35]", line)

    if "سی گیگ" in line:
        return re.sub(r"✅", "✅  [45]", line)

    if "چهل گیگ" in line and not any(phrase in line for phrase in ["صد و چهل گیگ", "صدو چهل گیگ", "صدوچهل گیگ"]):
        if any(day in line for day in ["شصد روز", "شصت روز"]):
            return re.sub(r"✅", "✅  [70]", line)
        return re.sub(r"✅", "✅  [55]", line)

    if "پنجاه گیگ" in line and not any(phrase in line for phrase in ["صد و پنجاه گیگ", "صدو پنجاه گیگ", "صدوپنجاه گیگ"]):
        return re.sub(r"✅", "✅  [65]", line)

    if any(gig in line for gig in ["شصت گیگ", "شصد گیگ"]) and \
       not any(phrase in line for phrase in ["صد و شصت گیگ", "صدو شصت گیگ", "صدوشصت گیگ"]):
        if "نود روز" in line:
            return re.sub(r"✅", "✅  [105]", line)
        elif any(day in line for day in ["شصت روز", "شصد روز"]):
            return re.sub(r"✅", "✅  [90]", line)
        return re.sub(r"✅", "✅  [78]", line)

    if "هفتاد گیگ" in line:
        return re.sub(r"✅", "✅  [91]", line)

    if "هشتاد گیگ" in line and not any(phrase in line for phrase in ["صد و هشتاد گیگ", "صدو هشتاد گیگ", "صدوهشتاد گیگ"]):
        if any(day in line for day in ["شصت روز", "شصد روز"]):
            return re.sub(r"✅", "✅  [110]", line)
        return re.sub(r"✅", "✅  [104]", line)

    if "نود گیگ" in line:
        if "نود روز" in line:
            return re.sub(r"✅", "✅  [135]", line)
        return re.sub(r"✅", "✅  [117]", line)

    if "صد گیگ" in line:
        if "نود روز" in line:
            return re.sub(r"✅", "✅  [150]", line)
        return re.sub(r"✅", "✅  [130]", line)

    if any(phrase in line for phrase in ["صد و بیست گیگ", "صدو بیست گیگ", "صدوبیست گیگ"]):
        if any(day in line for day in ["صد و بیست روز", "صدو بیست روز", "صدوبیست روز"]):
            return re.sub(r"✅", "✅  [180]", line)
        elif "نود روز" in line:
            return re.sub(r"✅", "✅  [165]", line)
        return re.sub(r"✅", "✅  [156]", line)

    if any(phrase in line for phrase in ["صد و پنجاه گیگ", "صدو پنجاه گیگ", "صدوپنجاه گیگ"]):
        return re.sub(r"✅", "✅  [195]", line)

    if "🟢" in line:
        return line.replace("🟢", "🟢  [000000]")

    return line

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
