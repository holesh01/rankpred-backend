// // ---------------- NAVIGATION ----------------
// function goBack() {
//   window.location.href = "index.html";
// }

// // ---------------- LOAD EXAM ----------------
// document.addEventListener("DOMContentLoaded", () => {
//   const exam = localStorage.getItem("selectedExam");
//   const title = document.getElementById("examTitle");
//   if (title && exam) {
//     title.textContent = exam + " Evaluation";
//   }
// });

// // ---------------- SUBMIT EVALUATION ----------------
// async function submitEvaluation() {
//   const exam = localStorage.getItem("selectedExam");
//   const fileInput = document.getElementById("responseFile");

//   if (!exam || !fileInput.files.length) {
//     alert("Missing exam or file");
//     return;
//   }

//   const formData = new FormData();
//   formData.append("exam_name", exam);
//   formData.append("name", document.getElementById("name").value);
//   formData.append("roll", document.getElementById("roll").value);
//   formData.append("category", document.getElementById("category").value);
//   formData.append("gender", document.getElementById("gender").value);
//   formData.append("state", document.getElementById("state").value);
//   formData.append("file", fileInput.files[0]);

//   try {
//     const res = await fetch("http://127.0.0.1:5000/evaluate", {
//       method: "POST",
//       body: formData
//     });

//     if (!res.ok) {
//       throw new Error("Backend error");
//     }

//     document.getElementById("status").textContent =
//       "Evaluation saved successfully";

//   } catch (err) {
//     document.getElementById("status").textContent =
//       "Evaluation failed";
//   }
// }
// ---------------- NAVIGATION ----------------
function goBack() {
  window.location.href = "index.html";
}

// ---------------- LOAD EXAM ----------------
document.addEventListener("DOMContentLoaded", () => {
  const exam = localStorage.getItem("selectedExam");
  const title = document.getElementById("examTitle");
  if (title && exam) {
    title.textContent = exam + " Evaluation";
  }
});

// ---------------- SUBMIT EVALUATION ----------------
async function submitEvaluation() {
  const exam = localStorage.getItem("selectedExam");
  const fileInput = document.getElementById("responseFile");

  const name = document.getElementById("name").value.trim();
  const roll = document.getElementById("roll").value.trim();
  const category = document.getElementById("category").value;
  const gender = document.getElementById("gender").value;
  const state = document.getElementById("state").value;

  if (!exam || !fileInput.files.length ||
      !name || !roll || !category || !gender || !state) {
    alert("Please fill all fields");
    return;
  }

  const formData = new FormData();
  formData.append("exam_name", exam);
  formData.append("name", name);
  formData.append("roll", roll);
  formData.append("category", category);
  formData.append("gender", gender);
  formData.append("state", state);
  formData.append("file", fileInput.files[0]);

  // 🔹 fire backend request (do not block redirect)
  fetch("http://127.0.0.1:5000/evaluate", {
    method: "POST",
    body: formData
  }).catch(() => {
    console.warn("Evaluation request failed");
  });

  // ✅ ALWAYS redirect
  const examKey = exam.replaceAll(" ", "_");

  window.location.href =
    `result.html?exam=${encodeURIComponent(examKey)}&roll=${encodeURIComponent(roll)}`;


}
const subjects = [];

document.querySelectorAll("#subjectTable tbody tr").forEach(row => {
  const name = row.querySelector(".sub-name").value;
  const maxMarks = parseInt(row.querySelector(".sub-marks").value);
  const countInTotal = row.querySelector(".sub-count").checked;

  subjects.push({
    name: name,
    max_marks: maxMarks,
    count_in_total: countInTotal
  });
});

function addSubjectRow() {
  const table = document.querySelector("#subjectTable tbody");

  const row = document.createElement("tr");
  row.innerHTML = `
        <td><input type="text" class="sub-name" placeholder="e.g. Computer" required></td>
        <td><input type="number" class="sub-marks" placeholder="50" required></td>
        <td style="text-align:center">
          <input type="checkbox" class="sub-count" checked>
        </td>
        <td>
          <button onclick="this.closest('tr').remove()">Remove</button>
        </td>`;
  table.appendChild(row);
}
