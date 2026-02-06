from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import shutil
import re
from bs4 import BeautifulSoup
from openpyxl import Workbook, load_workbook
import requests

app = Flask(__name__)
CORS(app)

BASE_DIR = "data"
UPLOAD_DIR = "uploads"

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ---------------- BASIC ----------------
@app.route("/")
def home():
    return "Backend running"


def safe_name(name):
    return name.replace(" ", "_")


# ---------------- ADMIN: LIST EXAMS ----------------
@app.route("/admin/exams", methods=["GET"])
def admin_list_exams():
    exams = []

    for folder in os.listdir(BASE_DIR):
        exam_dir = os.path.join(BASE_DIR, folder)
        scheme_path = os.path.join(exam_dir, "marking_scheme.xlsx")

        if not os.path.isdir(exam_dir) or not os.path.exists(scheme_path):
            continue

        wb = load_workbook(scheme_path)
        ws = wb.active

        scheme = {}
        for row in ws.iter_rows(min_row=2, values_only=True):
            scheme[row[0]] = row[1]

        exams.append({
            "exam_name": scheme.get("Exam Name"),
            "correct": scheme.get("Correct"),
            "wrong": scheme.get("Wrong"),
            "na": scheme.get("NA")
        })

    return jsonify(exams)


# ---------------- ADMIN: CREATE EXAM ----------------
@app.route("/admin/create-exam", methods=["POST"])
def create_exam():
    data = request.json

    exam_name = data.get("exam_name")
    correct = data.get("correct")
    wrong = data.get("wrong")
    na = data.get("na")
    subjects = data.get("subjects", [])

    if not exam_name:
        return jsonify({"error": "exam_name required"}), 400

    if not subjects:
        return jsonify({"error": "subjects required"}), 400

    exam_dir = os.path.join(BASE_DIR, safe_name(exam_name))
    os.makedirs(exam_dir, exist_ok=True)

    # ---- marking_scheme.xlsx ----
    scheme_path = os.path.join(exam_dir, "marking_scheme.xlsx")
    wb = Workbook()
    ws = wb.active
    ws.title = "scheme"
    ws.append(["Key", "Value"])
    ws.append(["Exam Name", exam_name])
    ws.append(["Correct", correct])
    ws.append(["Wrong", wrong])
    ws.append(["NA", na])
    wb.save(scheme_path)

    # ---- subjects.xlsx ----
    subjects_path = os.path.join(exam_dir, "subjects.xlsx")
    wb_sub = Workbook()
    ws_sub = wb_sub.active
    ws_sub.title = "subjects"
    ws_sub.append(["Subject Name", "Max Marks", "Count In Total"])

    for sub in subjects:
        ws_sub.append([
            sub["name"],
            sub["max_marks"],
            "YES" if sub["count_in_total"] else "NO"
        ])

    wb_sub.save(subjects_path)

    # ---- responses.xlsx ----
    response_path = os.path.join(exam_dir, "responses.xlsx")
    wb2 = Workbook()
    ws2 = wb2.active
    ws2.title = "responses"

    header = ["Name", "Roll", "Category", "Gender", "State", "Final Marks"]
    for sub in subjects:
        header.append(sub["name"])

    ws2.append(header)
    wb2.save(response_path)

    return jsonify({"status": "success", "exam": exam_name})


# ---------------- ADMIN: DELETE EXAM ----------------
@app.route("/admin/delete-exam", methods=["POST"])
def delete_exam():
    data = request.json
    exam_name = data.get("exam_name")

    if not exam_name:
        return jsonify({"error": "exam_name required"}), 400

    exam_dir = os.path.join(BASE_DIR, safe_name(exam_name))
    if not os.path.exists(exam_dir):
        return jsonify({"error": "exam not found"}), 404

    shutil.rmtree(exam_dir)
    return jsonify({"status": "deleted"})


# ---------------- READ MARKING SCHEME ----------------
def read_marking_scheme(exam_name):
    path = os.path.join(BASE_DIR, safe_name(exam_name), "marking_scheme.xlsx")
    wb = load_workbook(path)
    ws = wb.active

    scheme = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        scheme[row[0]] = row[1]
    return scheme


# ---------------- READ SUBJECT CONFIG ----------------
def read_subjects(exam_name):
    path = os.path.join(BASE_DIR, safe_name(exam_name), "subjects.xlsx")
    wb = load_workbook(path)
    ws = wb.active

    subjects = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        subjects.append({
            "name": row[0],
            "max_marks": row[1],
            "count_in_total": True if row[2] == "YES" else False
        })
    return subjects



# ---------------- PARSE RESPONSE ----------------
# def parse_response_sectionwise(html_path, scheme, subjects):
#     section_map = {}
#     section_order = []
#     current_section = None

#     with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
#         soup = BeautifulSoup(f, "lxml")

#     for el in soup.find_all("div"):
#         if el.get("class") == ["section-lbl"]:
#             current_section = el.get_text(strip=True)
#             if current_section not in section_map:
#                 section_map[current_section] = {"c": 0, "w": 0, "n": 0}
#                 section_order.append(current_section)

#         if el.get("class") == ["question-pnl"] and current_section:
#             chosen = None
#             correct_option = None

#             chosen_row = el.find("td", string=re.compile("Chosen Option"))
#             if chosen_row:
#                 v = chosen_row.find_next_sibling("td").get_text(strip=True)
#                 if v != "--":
#                     chosen = int(v)

#             right_td = el.find("td", class_="rightAns")
#             if right_td:
#                 m = re.search(r"(\d)\.", right_td.get_text())
#                 if m:
#                     correct_option = int(m.group(1))

#             if chosen is None:
#                 section_map[current_section]["n"] += 1
#             elif chosen == correct_option:
#                 section_map[current_section]["c"] += 1
#             else:
#                 section_map[current_section]["w"] += 1

#     subject_results = []
#     final_marks = 0

#     for idx, sec in enumerate(section_order):
#         c = section_map[sec]["c"]
#         w = section_map[sec]["w"]
#         n = section_map[sec]["n"]

#         marks = (
#             c * scheme["Correct"]
#             + w * scheme["Wrong"]
#             + n * scheme["NA"]
#         )

#         sub = subjects[idx]

#         subject_results.append({
#             "name": sub["name"],
#             "marks": marks,
#             "count_in_total": sub["count_in_total"]
#         })

#         if sub["count_in_total"]:
#             final_marks += marks

#     return final_marks, subject_results

def parse_response_sectionwise_from_html(html_content, scheme, subjects):
    section_map = {}
    section_order = []
    current_section = None

    soup = BeautifulSoup(html_content, "lxml")

    for el in soup.find_all("div"):
        if el.get("class") == ["section-lbl"]:
            current_section = el.get_text(strip=True)
            if current_section not in section_map:
                section_map[current_section] = {"c": 0, "w": 0, "n": 0}
                section_order.append(current_section)

        if el.get("class") == ["question-pnl"] and current_section:
            chosen = None
            correct_option = None

            chosen_row = el.find("td", string=re.compile("Chosen Option"))
            if chosen_row:
                v = chosen_row.find_next_sibling("td").get_text(strip=True)
                if v != "--":
                    chosen = int(v)

            right_td = el.find("td", class_="rightAns")
            if right_td:
                m = re.search(r"(\d)\.", right_td.get_text())
                if m:
                    correct_option = int(m.group(1))

            if chosen is None:
                section_map[current_section]["n"] += 1
            elif chosen == correct_option:
                section_map[current_section]["c"] += 1
            else:
                section_map[current_section]["w"] += 1

    subject_results = []
    final_marks = 0

    for idx, sec in enumerate(section_order):
        c = section_map[sec]["c"]
        w = section_map[sec]["w"]
        n = section_map[sec]["n"]

        marks = (
            c * scheme["Correct"]
            + w * scheme["Wrong"]
            + n * scheme["NA"]
        )

        sub = subjects[idx]

        subject_results.append({
            "name": sub["name"],
            "marks": marks,
            "count_in_total": sub["count_in_total"]
        })

        if sub["count_in_total"]:
            final_marks += marks

    return final_marks, subject_results

# ---------------- SAVE RESULT ----------------
def save_user_result(exam_name, base_data, subject_results):
    path = os.path.join(BASE_DIR, safe_name(exam_name), "responses.xlsx")
    wb = load_workbook(path)
    ws = wb.active

    headers = [c.value for c in ws[1]]

    row = base_data[:]
    for sub in subject_results:
        row.append(sub["marks"])

    ws.append(row)
    wb.save(path)


# ---------------- EVALUATE ----------------
@app.route("/evaluate", methods=["POST"])
def evaluate_exam():
    exam_name = request.form.get("exam_name")
    name = request.form.get("name")
    roll = request.form.get("roll")
    category = request.form.get("category")
    gender = request.form.get("gender")
    state = request.form.get("state")
    file = request.files.get("file")

    if not all([exam_name, name, roll, category, gender, state, file]):
        return jsonify({"error": "Missing fields"}), 400

    upload_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(upload_path)

    scheme = read_marking_scheme(exam_name)
    subjects = read_subjects(exam_name)

    with open(upload_path, "r", encoding="utf-8", errors="ignore") as f:html_content = f.read()

    final_marks, subject_results = parse_response_sectionwise_from_html(html_content, scheme, subjects
)


    save_user_result(
        exam_name,
        [name, roll, category, gender, state, final_marks],
        subject_results
    )

    return jsonify({"status": "saved", "final_marks": final_marks})
@app.route("/evaluate-from-url", methods=["POST"])
def evaluate_exam_from_url():
    data = request.json

    exam_name = data.get("exam_name")
    category = data.get("category")
    gender = data.get("gender")
    state = data.get("state")
    url = data.get("url")

    if not all([exam_name, category, gender, state, url]):
        return jsonify({"error": "Missing fields"}), 400

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=20)

        if response.status_code != 200:
            return jsonify({"error": "Unable to fetch DigiALM page"}), 400

        html_content = response.text

        # 🔥 AUTO-EXTRACT DETAILS
        details = extract_candidate_details(html_content)

        if not details["roll"] or not details["name"]:
            return jsonify({"error": "Unable to extract candidate details"}), 400

        scheme = read_marking_scheme(exam_name)
        subjects = read_subjects(exam_name)

        final_marks, subject_results = parse_response_sectionwise_from_html(
            html_content, scheme, subjects
        )

        save_user_result(
            exam_name,
            [
                details["name"],
                details["roll"],
                category,
                gender,
                state,
                final_marks
            ],
            subject_results
        )

        return jsonify({
            "status": "saved",
            "final_marks": final_marks,
            "candidate": details
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_candidate_details(html_content):
    soup = BeautifulSoup(html_content, "lxml")

    details = {
        "roll": None,
        "name": None,
        "venue": None,
        "exam_date": None,
        "exam_time": None,
        "subject": None
    }

    # DigiALM header table
    for row in soup.select("table tr"):
        cells = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cells) != 2:
            continue

        key, value = cells

        if "Roll Number" in key:
            details["roll"] = value
        elif "Candidate Name" in key:
            details["name"] = value
        elif "Venue Name" in key:
            details["venue"] = value
        elif "Exam Date" in key:
            details["exam_date"] = value
        elif "Exam Time" in key:
            details["exam_time"] = value
        elif "Subject" in key:
            details["subject"] = value

    return details


# ---------------- RESULT API ----------------
@app.route("/result")
def get_result():
    exam = request.args.get("exam")
    roll = request.args.get("roll")

    if not exam or not roll:
        return jsonify({"error": "Missing exam or roll"}), 400

    path = os.path.join(BASE_DIR, safe_name(exam), "responses.xlsx")
    if not os.path.exists(path):
        return jsonify({"error": "Result not found"}), 404

    wb = load_workbook(path)
    ws = wb.active
    headers = [c.value for c in ws[1]]
    col = {h: i for i, h in enumerate(headers)}

    row = None
    for r in ws.iter_rows(min_row=2, values_only=True):
        if str(r[col["Roll"]]) == str(roll):
            row = r
            break

    if not row:
        return jsonify({"error": "Candidate not found"}), 404

    subjects_cfg = read_subjects(exam)

    counted = []
    qualifying = []
    final_marks = 0

    for sub in subjects_cfg:
        marks = row[col[sub["name"]]]
        item = {"name": sub["name"], "marks": marks}

        if sub["count_in_total"]:
            counted.append(item)
            final_marks += marks
        else:
            qualifying.append(item)

    return jsonify({
        "exam": exam,
        "candidate": {
            "name": row[col["Name"]],
            "roll": row[col["Roll"]],
            "category": row[col["Category"]],
            "gender": row[col["Gender"]],
            "state": row[col["State"]]
        },
        "counted_subjects": counted,
        "qualifying_subjects": qualifying,
        "final_marks": final_marks
    })


# ---------------- START ----------------
if __name__ == "__main__":
    app.run(debug=True)
