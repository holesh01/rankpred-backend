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
const API_BASE = "https://rankpred-backend-1.onrender.com";

// ---------------- SUBMIT EVALUATION ----------------
async function submitEvaluation() {
  const exam = localStorage.getItem("selectedExam");

  const fileInput = document.getElementById("responseFile");
  const urlInput = document.getElementById("resultUrl");

  const category = document.getElementById("category").value;
  const gender = document.getElementById("gender").value;
  const state = document.getElementById("state").value;

  const statusEl = document.getElementById("status");
  statusEl.textContent = "";

  if (!exam || !category || !gender || !state) {
    alert("Please select Category, Gender and State");
    return;
  }

  const hasFile = fileInput && fileInput.files.length > 0;
  const hasUrl = urlInput && urlInput.value.trim() !== "";

  if (!hasFile && !hasUrl) {
    alert("Upload response file OR paste DigiALM result link");
    return;
  }

  statusEl.textContent = "Evaluating...";

  try {
    let res;

    // ---------------- FILE FLOW (OPTIONAL / LEGACY) ----------------
    if (hasFile) {
      const formData = new FormData();
      formData.append("exam_name", exam);
      formData.append("category", category);
      formData.append("gender", gender);
      formData.append("state", state);
      formData.append("file", fileInput.files[0]);

      res = await fetch(`${API_BASE}/evaluate-from-url`, {
        method: "POST",
        body: formData
      });

    // ---------------- URL FLOW (PRIMARY) ----------------
    } else {
      res = await fetch(`${API_BASE}/evaluate-from-url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          exam_name: exam,
          category,
          gender,
          state,
          url: urlInput.value.trim()
        })
      });
    }

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || "Evaluation failed");
    }

    statusEl.textContent = "Evaluation saved successfully";

    // 🔥 Roll number comes from backend extraction
    const roll = data.candidate?.roll;
    if (!roll) {
      throw new Error("Roll number not found in response sheet");
    }

    // ✅ Redirect AFTER success
    window.location.href =
      `result.html?exam=${encodeURIComponent(exam)}&roll=${encodeURIComponent(roll)}`;

  } catch (err) {
    console.error(err);
    statusEl.textContent = "Evaluation failed: " + err.message;
  }
}
