document.addEventListener("DOMContentLoaded", () => {
  // Feather icons
  if (window.feather) {
    window.feather.replace();
  }

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute("href")).scrollIntoView({
        behavior: "smooth",
      });
    });
  });

  // Countdown Timer
  const countdownEl = document.getElementById("countdown");
  const startDate = countdownEl?.dataset.start;

  if (countdownEl && startDate) {
    const eventDate = new Date(startDate).getTime();

    function updateCountdown() {
      const now = new Date().getTime();
      const distance = eventDate - now;

      if (distance <= 0) {
        countdownEl.innerHTML = "🎉 Event Started!";
        return;
      }

      const days = Math.floor(distance / (1000 * 60 * 60 * 24));
      const hours = Math.floor(
        (distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
      );
      const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((distance % (1000 * 60)) / 1000);

      countdownEl.innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s`;
    }

    updateCountdown();
    setInterval(updateCountdown, 1000);
  }

  // Theme Switcher
  const themeToggle = document.getElementById("theme-toggle");
  const htmlEl = document.documentElement;

  const setDarkTheme = () => {
    htmlEl.classList.add("dark");
    themeToggle.innerHTML = '<i data-feather="sun"></i>';
    feather.replace();
    localStorage.setItem("theme", "dark");
  };

  const setLightTheme = () => {
    htmlEl.classList.remove("dark");
    themeToggle.innerHTML = '<i data-feather="moon"></i>';
    feather.replace();
    localStorage.setItem("theme", "light");
  };

  if (localStorage.getItem("theme") === "dark") {
    setDarkTheme();
  } else {
    setLightTheme();
  }

  themeToggle.addEventListener("click", () => {
    if (htmlEl.classList.contains("dark")) {
      setLightTheme();
    } else {
      setDarkTheme();
    }
  });
});