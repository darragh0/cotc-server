document.addEventListener("DOMContentLoaded", () => {
  const resetButton = document.getElementById("reset-filters");
  const clearFiltersButton = document.getElementById("clear-filters");
  const filterForm = document.getElementById("filter-form");

  document.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      filterForm.submit();
    }
  });

  resetButton.addEventListener("click", () => {
    document.getElementById("device-filter").value = "";
    document.getElementById("start-time").value = "";
    document.getElementById("end-time").value = "";
    document.getElementById("filter-form").submit();
  });

  clearFiltersButton.addEventListener("click", () =>
    window.location.href = window.location.pathname
  );

  filterForm.addEventListener("submit", (event) => {
    const startTime = document.getElementById("start-time").value;
    const endTime = document.getElementById("end-time").value;

    if (startTime && endTime && new Date(startTime) > new Date(endTime)) {
      event.preventDefault();
      alert("Start time cannot be later than end time");
    }
  });
});
