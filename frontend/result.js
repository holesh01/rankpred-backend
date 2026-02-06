function goHome() {
  window.location.href = "index.html";
}

const statusMsg = document.getElementById("statusMsg");

const params = new URLSearchParams(window.location.search);
const exam = params.get("exam");
const roll = params.get("roll");

if (!exam || !roll) {
  statusMsg.textContent = "Result details not provided.";
} else {
  fetch(
    `http://127.0.0.1:5000/result?exam=${encodeURIComponent(exam)}&roll=${encodeURIComponent(roll)}`
  )
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        statusMsg.textContent = data.error;
        return;
      }

      // ---------- BASIC INFO ----------
      statusMsg.style.display = "none";

      document.getElementById("examName").textContent =
        data.exam.replaceAll("_", " ");

      document.getElementById("rName").textContent =
        data.candidate.name;

      document.getElementById("rRoll").textContent =
        data.candidate.roll;

      document.getElementById("rCategory").textContent =
        data.candidate.category;

      document.getElementById("rState").textContent =
        data.candidate.state;

      // ---------- COUNTED SUBJECTS ----------
      const countedBody = document.getElementById("countedTableBody");
      countedBody.innerHTML = "";

      data.counted_subjects.forEach(sub => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${sub.name}</td>
          <td>${sub.marks}</td>
        `;
        countedBody.appendChild(tr);
      });

      // ---------- FINAL MARKS ----------
      document.getElementById("finalMarks").textContent =
        data.final_marks;

      // ---------- QUALIFYING SUBJECTS ----------
      const qualifyingSection = document.getElementById("qualifyingSection");
      const qualBody = document.getElementById("qualifyingTableBody");
      qualBody.innerHTML = "";

      if (data.qualifying_subjects.length > 0) {
        qualifyingSection.style.display = "block";

        data.qualifying_subjects.forEach(sub => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td>${sub.name}</td>
            <td>${sub.marks}</td>
          `;
          qualBody.appendChild(tr);
        });
      } else {
        qualifyingSection.style.display = "none";
      }
    })
    .catch(err => {
      console.error(err);
      statusMsg.textContent =
        "Result not available yet. Please try again later.";
    });
}
