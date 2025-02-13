import re

def remove_titles(line):
    title_pattern = r"^Saeid Barati, \[(\d{2}-\w{3}-\d{2}) \d{2}:\d{2}\]$"
    match = re.match(title_pattern, line.strip())
    if match:
        return "", match.group(1)
    return line, None

def process_text(line, counts):
    if not any(keyword in line for keyword in ["تمدید شد ✅", "تمدید شد✅", "🟢"]):
        return None  # فقط خطوط حاوی این عبارات پردازش می‌شوند
    
    if "شصد گیگ" in line:
        if "سی روز" in line:
            line = line.replace("✅", "✅  [78]")
        elif "شصد روز" in line:
            line = line.replace("✅", "✅  [90]")
        elif "نود روز" in line:
            line = line.replace("✅", "✅  [105]")
        else:
            line = line.replace("✅", "✅  [000000]")
    
    if "هفتاد گیگ" in line:
        if "سی روز" in line:
            line = line.replace("✅", "✅  [91]")
        else:
            line = line.replace("✅", "✅  [000000]")
    
    if "هشتاد گیگ" in line:
        if "سی روز" in line:
            line = line.replace("✅", "✅  [104]")
        elif "شصد روز" in line:
            line = line.replace("✅", "✅  [110]")
        else:
            line = line.replace("✅", "✅  [000000]")
    
    if "نود گیگ" in line:
        if "سی روز" in line:
            line = line.replace("✅", "✅  [117]")
        elif "شصد روز" in line:
            line = line.replace("✅", "✅  [125]")
        elif "نود روز" in line:
            line = line.replace("✅", "✅  [135]")
        else:
            line = line.replace("✅", "✅  [000000]")
    
    if "صد گیگ" in line:
        if "سی روز" in line or "شصد روز" in line:
            line = line.replace("✅", "✅  [130]")
        elif "نود روز" in line:
            line = line.replace("✅", "✅  [150]")
        else:
            line = line.replace("✅", "✅  [000000]")
    
    if "صد و بیست گیگ" in line:
        if "سی روز" in line or "شصد روز" in line:
            line = line.replace("✅", "✅  [156]")
        elif "نود روز" in line:
            line = line.replace("✅", "✅  [165]")
        else:
            line = line.replace("✅", "✅  [000000]")
    
    if "صد و پنجاه گیگ" in line:
        if "سی روز" in line or "شصد روز" in line or "نود روز" in line:
            line = line.replace("✅", "✅  [195]")
        else:
            line = line.replace("✅", "✅  [000000]")
    
    replacements = {
        "ده گیگ": "✅  [25]",
        "بیست گیگ": "✅  [35]",
        "سی گیگ": "✅  [45]",
        "چهل گیگ": "✅  [55]",
        "پنجاه گیگ": "✅  [65]",
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
        
        processed_line = process_text(line, counts)
        if processed_line:
            processed_lines.append(processed_line)
            
            if "[000000]" in processed_line:
                review_lines.append(processed_line)
            
            matches = re.findall(r"\[(\d+)\]", processed_line)
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
