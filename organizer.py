import json
import re
import os

def restructure_data(input_file, output_file):
    print("Reading file... please wait (this is a large file)")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # This part "hunts" for the data block inside the HTML code
    try:
        match = re.search(r'const\s+COURSE_DATA\s*=\s*({.*?});', content, re.DOTALL)
        if not match:
            # Try a second way if the first one fails
            match = re.search(r'var\s+COURSE_DATA\s*=\s*({.*?});', content, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            data = json.loads(json_str)
        else:
            print("Error: Could not find the data block 'COURSE_DATA' inside the file.")
            return
    except Exception as e:
        print(f"Error parsing data: {e}")
        return

    restructured = {
        "Main": [],
        "PYQ": {},
        "GRP": [],
        "CustomPool": []
    }

    # FMGE Weightage (Ref Page 6)
    weightage_map = {
        "Surgery": 0.15, "OBGYN": 0.15, "Medicine": 0.15, "PSM": 0.10, 
        "Pathology": 0.08, "Pharmacology": 0.08, "Microbiology": 0.07, 
        "Anatomy": 0.06, "Physiology": 0.06, "Biochemistry": 0.05, "Pediatrics": 0.05
    }

    print("Sorting 28,000+ questions...")
    for category in data.get('categories', []):
        cat_name = category.get('categoryName', '')
        for subject in category.get('subjects', []):
            sub_name = subject.get('subjectName', '')
            for module in subject.get('modules', []):
                mod_name = module.get('moduleName', '')
                year_match = re.search(r'20\d{2}', mod_name)
                
                for q in module.get('questions', []):
                    q_data = {
                        "id": q.get('id'),
                        "subject": sub_name,
                        "module": mod_name,
                        "question": q.get('html_qtxt'),
                        "options": q.get('options'),
                        "answer_idx": q.get('corr_idx'),
                        "explanation": q.get('html_expl'),
                        "weight": weightage_map.get(sub_name, 0.03)
                    }

                    # Logic to sort into your 4 sections (Ref Page 1)
                    if year_match or "PYQ" in cat_name.upper():
                        year = year_match.group(0) if year_match else "General"
                        if year not in restructured["PYQ"]: restructured["PYQ"][year] = []
                        restructured["PYQ"][year].append(q_data)
                    elif "GRP" in cat_name.upper():
                        restructured["GRP"].append(q_data)
                    else:
                        restructured["Main"].append(q_data)
                    
                    restructured["CustomPool"].append(q_data)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(restructured, f, indent=4)
    
    print(f"Done! Created '{output_file}' with {len(restructured['CustomPool'])} questions.")

# Start the process
restructure_data('FMGE Q-Bank t.txt', 'Restructured_FMGE_Bank.json')