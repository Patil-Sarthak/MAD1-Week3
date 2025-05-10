from jinja2 import Template, Environment
import matplotlib.pyplot as plt
import csv
import os
from jinja2.utils import htmlsafe_json_dumps

# Load CSV data
with open('data.csv') as f:
    reader = csv.reader(f)
    rows = [row for row in reader if len(row) >= 3][1:]  # Skip header

#  student & course IDs
student_ids = sorted(set(row[0] for row in rows))
course_ids = sorted(set(row[1] for row in rows))

# Prepare data
student_data = {}
course_data = {}

for sid, cid, marks in rows:
    marks = int(marks)
    student_data.setdefault(sid, []).append((cid, marks))
    course_data.setdefault(cid, []).append(marks)

# Generate histograms for each course
for cid, marks in course_data.items():
    plt.figure(figsize=(6, 4))
    plt.hist(marks, bins=5, color='skyblue', edgecolor='black')
    plt.title(f"Histogram for {cid}")
    plt.xlabel('Marks')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(f"hist_{cid}.png")
    plt.close()

# HTML Template
template_str = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Student & Course Dashboard</title>
    <style>
        body { margin: 0; font-family: Arial, sans-serif; display: flex; height: 100vh; }
        .sidebar {
            width: 250px;
            background: #1f1f1f;
            color: #fff;
            padding: 20px;
            overflow-y: auto;
        }
        .sidebar h3 { margin-top: 20px; border-bottom: 1px solid #444; padding-bottom: 5px; }
        .item { cursor: pointer; margin: 5px 0; padding: 5px; border-radius: 4px; transition: background 0.3s; }
        .item:hover { background: #333; }
        .search {
            width: 100%; padding: 5px; margin-bottom: 10px; border: none;
            border-radius: 4px; font-size: 14px;
        }
        .content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f9f9f9;
            transition: all 0.3s;
        }
        table { border-collapse: collapse; width: 100%; margin-top: 10px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
        img { margin-top: 10px; max-width: 100%; }
    </style>
</head>
<body>
    <div class="sidebar">
        <input type="text" id="searchBox" class="search" placeholder="Search IDs..." onkeyup="filterList()">
        <h3>Students</h3>
        <div id="students">
            {% for sid in student_ids %}
                <div class="item" onclick="showStudent('{{ sid }}')">{{ sid }}</div>
            {% endfor %}
        </div>
        <h3>Courses</h3>
        <div id="courses">
            {% for cid in course_ids %}
                <div class="item" onclick="showCourse('{{ cid }}')">{{ cid }}</div>
            {% endfor %}
        </div>
    </div>
    <div class="content" id="result">
        <h2>📊 Select a student or course ID to view details.</h2>
    </div>

    <script>
        const studentData = {{ student_data | tojson }};
        const courseData = {{ course_data | tojson }};

        function showStudent(sid) {
            const list = studentData[sid];
            let total = 0;
            let html = `<h2>🎓 Student ID: ${sid}</h2><table><tr><th>Course</th><th>Marks</th></tr>`;
            for (const [cid, mark] of list) {
                html += `<tr><td>${cid}</td><td>${mark}</td></tr>`;
                total += mark;
            }
            html += `<tr><td><strong>Total</strong></td><td><strong>${total}</strong></td></tr></table>`;
            document.getElementById("result").innerHTML = html;
        }

        function showCourse(cid) {
            const marks = courseData[cid];
            const total = marks.reduce((a, b) => a + b, 0);
            const avg = (total / marks.length).toFixed(2);
            const max = Math.max(...marks);
            let html = `<h2>📘 Course ID: ${cid}</h2>
                        <p><strong>Average:</strong> ${avg}</p>
                        <p><strong>Maximum:</strong> ${max}</p>
                        <img src="hist_${cid}.png" alt="Histogram for ${cid}">`;
            document.getElementById("result").innerHTML = html;
        }

        function filterList() {
            const filter = document.getElementById('searchBox').value.toLowerCase();
            ['students', 'courses'].forEach(section => {
                const items = document.getElementById(section).getElementsByClassName('item');
                for (let i = 0; i < items.length; i++) {
                    const txt = items[i].innerText.toLowerCase();
                    items[i].style.display = txt.includes(filter) ? "" : "none";
                }
            });
        }
    </script>
</body>
</html>
'''

# Render with Jinja2
env = Environment()
env.filters['tojson'] = lambda v: htmlsafe_json_dumps(v)
template = env.from_string(template_str)

output_html = template.render(
    student_ids=student_ids,
    course_ids=course_ids,
    student_data=student_data,
    course_data=course_data,
)

# Save index.html
with open("output.html", "w", encoding="utf-8") as f:
    f.write(output_html)

print("✅ output.html created successfully.")
