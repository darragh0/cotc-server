const UPDATE_THRESHOLD_MS = 5000;
const NOTIFICATION_DURATION_MS = 2500;
const POLL_INTERVAL_MS = 5000;

function checkForUpdates() {
  fetch("/check_update")
    .then((response) => response.json())
    .then((data) => {
      const lastUpdateTime = new Date(data.last_update);
      const currentTime = new Date();

      // If the last update is newer than the current time by a threshold (e.g., 5 seconds)
      if (currentTime - lastUpdateTime < UPDATE_THRESHOLD_MS) {
        document.querySelector(".update-notification").classList.add("active");
        // Briefly display update notification
        setTimeout(() => location.reload(), NOTIFICATION_DURATION_MS);
      }
    })
    .catch(error => console.error("Error checking for updates:", error));
}

// Poll every 10 seconds
setInterval(checkForUpdates, POLL_INTERVAL_MS);
