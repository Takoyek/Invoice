import re

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

def main():
    input_path = "D:\\AVIDA\\CODE\\Invoice\\Input.txt"
    output_path = "D:\\AVIDA\\CODE\\Invoice\\Output.txt"
    editme_path = "D:\\AVIDA\\CODE\\Invoice\\EditMe.txt"

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

if __name__ == "__main__":
    main()
