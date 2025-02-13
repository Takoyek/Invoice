import re

def remove_titles(line):
    title_pattern = r"^Saeid Barati, \[(\d{2}-\w{3}-\d{2}) \d{2}:\d{2}\]$"
    match = re.match(title_pattern, line.strip())
    if match:
        return "", match.group(1)
    return line, None

def process_text(line, counts):
    replacements = {
        "ده گیگ": "✅  [25]",
        "بیست گیگ": "✅  [35]",
        "سی گیگ": "✅  [45]",
        "چهل گیگ": "✅  [55]",
        "پنجاه گیگ": "✅  [65]",
        "شصد گیگ": "✅  [000000]",
        "هفتاد گیگ": "✅  [000000]",
        "هشتاد گیگ": "✅  [000000]",
        "نود گیگ": "✅  [000000]",
        "صد گیگ": "✅  [000000]",
        "صدو بیست گیگ": "✅  [000000]",
        "صدو پنجاه گیگ": "✅  [000000]"
    }
    
    modified = False
    needs_review = False
    for key, value in replacements.items():
        if key in line:
            line = re.sub(r"✅", value, line)
            counts['total'] += 1
            modified = True
            if "000000" in value:
                needs_review = True
    
    if "🟢" in line:
        line = line.replace("🟢", "🟢  [000000]")
        counts['total'] += 1
        needs_review = True
        modified = True
    
    if modified:
        counts['actual_total'] += 1
    
    if needs_review:
        counts['needs_review'] += 1
    
    return line

def main():
    input_path = "D:\\AVIDA\\CODE\\Invoice\\Input.txt"
    output_path = "D:\\AVIDA\\CODE\\Invoice\\Output.txt"
    editme_path = "D:\\AVIDA\\CODE\\Invoice\\EditMe.txt"

    counts = {"total": 0, "needs_review": 0, "sum": 0, "actual_total": 0}
    processed_lines = []
    review_lines = []
    dates = []
    
    with open(input_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    for line in lines:
        line, date = remove_titles(line)
        if date:
            dates.append(date)
        
        if not any(keyword in line for keyword in ["تمدید شد ✅", "تمدید شد✅", "🟢"]):
            continue  # فقط خطوط حاوی این عبارات پردازش می‌شوند
        
        line = process_text(line, counts)
        processed_lines.append(line)
        
        if "[000000]" in line:
            review_lines.append(line)
        
        matches = re.findall(r"\[(\d+)\]", line)
        for match in matches:
            if match != "000000":
                counts['sum'] += int(match)
    
    start_date = min(dates) if dates else "نامشخص"
    end_date = max(dates) if dates else "نامشخص"
    
    processed_lines.append(f"\nبازه زمانی: {start_date} تا {end_date}\n")
    processed_lines.append(f"مجموع رکوردها: {counts['actual_total']} عدد\n")
    processed_lines.append(f"تعداد رکوردهایی که نیاز به بررسی دارد: {counts['needs_review']} عدد\n")
    processed_lines.append(f"جمع کل: {counts['sum']} هزار تومان\n")
    
    with open(output_path, "w", encoding="utf-8") as file:
        file.writelines(processed_lines)
    
    with open(editme_path, "w", encoding="utf-8") as file:
        file.writelines(review_lines)
        file.write(f"\nتعداد رکوردهایی که نیاز به بررسی دارد: {counts['needs_review']} عدد\n")
    
if __name__ == "__main__":
    main()
