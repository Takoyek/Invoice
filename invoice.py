import re

def remove_titles(line):
    # الگوی عناوین که باید حذف شود
    title_pattern = r"^Saeid Barati, \[\d{2}-\w{3}-\d{2} \d{2}:\d{2}\]$"
    if re.match(title_pattern, line.strip()):
        return ""
    return line

def process_text(line):
    # بررسی کلمه "سی" و افزودن عدد 45
    if "سی" in line:
        line = line.replace("✅", "✅45")
    # بررسی کلمه "پنجاه" و افزودن عدد 65
    if "پنجاه" in line:
        line = line.replace("✅", "✅65")
    # بررسی کلمه "Samadi" و افزودن عدد 45
    if "Samadi" in line:
        line = line.replace("🟢", "🟢 45")
    return line

def replace_numbers_with_brackets(line):
    # جایگذاری اعداد 45 و 65 داخل []
    for number in ["45", "65"]:
        line = line.replace(f"✅{number}", f"✅[{number}]")
        line = line.replace(f"🟢{number}", f"[ {number} ]🟢")
    return line

def main():
    input_path = "D:\\AVIDA\\CODE\\Invoice\\Input.txt"
    output_path = "D:\\AVIDA\\CODE\\Invoice\\Output.txt"

    with open(input_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    processed_lines = []
    for line in lines:
        line = remove_titles(line)
        if line.strip():  # بررسی اینکه خط خالی نباشد
            line = process_text(line)
            line = replace_numbers_with_brackets(line)
            processed_lines.append(line)

    with open(output_path, "w", encoding="utf-8") as file:
        file.writelines(processed_lines)

if __name__ == "__main__":
    main()
