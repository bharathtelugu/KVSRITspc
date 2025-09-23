// event_page.js
// JS for phased countdown, hero button, and FAQ accordion

document.addEventListener("DOMContentLoaded", function () {
  // --- 1. Phased Countdown & Button Logic ---
  const countdownSection = document.getElementById("countdown-section");
  if (countdownSection) {
    // Get dates from data attributes
    const regEndDate = new Date(countdownSection.dataset.regEnd).getTime();
    const eventStartDate = new Date(
      countdownSection.dataset.eventStart
    ).getTime();
    const revealTimeDate = new Date(
      countdownSection.dataset.revealTime
    ).getTime();

    // Get DOM elements to update
    const titleEl = document.getElementById("countdown-title");
    const buttonEl = document.getElementById("register-button");
    const daysEl = document.getElementById("days");
    const hoursEl = document.getElementById("hours");
    const minutesEl = document.getElementById("minutes");
    const secondsEl = document.getElementById("seconds");

    // Dot ring setup
    function setupDotRing(svgId, dots, color) {
      const svg = document.getElementById(svgId);
      svg.innerHTML = "";
      const r = 50,
        cx = 56,
        cy = 56;
      for (let i = 0; i < dots; i++) {
        const angle = (2 * Math.PI * i) / dots;
        const x = cx + r * Math.cos(angle);
        const y = cy + r * Math.sin(angle);
        const circle = document.createElementNS(
          "http://www.w3.org/2000/svg",
          "circle"
        );
        circle.setAttribute("cx", x);
        circle.setAttribute("cy", y);
        circle.setAttribute("r", 3.5);
        circle.setAttribute("fill", "#333");
        circle.setAttribute("class", "dot");
        svg.appendChild(circle);
      }
    }
    function updateDotRing(svgId, value, max, accent) {
      const svg = document.getElementById(svgId);
      const dots = svg.querySelectorAll(".dot");
      for (let i = 0; i < dots.length; i++) {
        dots[i].setAttribute("fill", i < value ? accent : "#333");
      }
    }
    setupDotRing("days-ring", 30, "#00FF85");
    setupDotRing("hours-ring", 24, "#00FF85");
    setupDotRing("minutes-ring", 60, "#00FF85");
    setupDotRing("seconds-ring", 60, "#00FF85");
    const accent = "#00FF85";

    const countdownInterval = setInterval(function () {
      const now = new Date().getTime();
      let targetDate, targetTitle;

      // --- This is the core logic ---
      if (now < regEndDate) {
        targetDate = regEndDate;
        targetTitle = "Registration Closes In:";
        // Button state
        if (buttonEl) {
          buttonEl.disabled = false;
          buttonEl.textContent = "Register Now";
          buttonEl.classList.remove("disabled");
        }
      } else if (now < eventStartDate) {
        targetDate = eventStartDate;
        targetTitle = "Event Starts In:";
        // Button state
        if (buttonEl) {
          buttonEl.disabled = true;
          buttonEl.textContent = "Registration Closed";
          buttonEl.classList.add("disabled");
        }
      } else if (now < revealTimeDate) {
        targetDate = revealTimeDate;
        targetTitle = "Problem Statements Reveal In:";
      } else {
        // Event is live or over
        titleEl.textContent = "The Event is Live!";
        document.getElementById("countdown").style.display = "none";
        clearInterval(countdownInterval);
        return;
      }

      // Update title
      titleEl.textContent = targetTitle;

      // Calculate distance
      const distance = targetDate - now;

      // Update timer values
      const days = Math.floor(distance / (1000 * 60 * 60 * 24));
      const hours = Math.floor(
        (distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
      );
      const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((distance % (1000 * 60)) / 1000);
      daysEl.textContent = days;
      hoursEl.textContent = hours;
      minutesEl.textContent = minutes;
      secondsEl.textContent = seconds;
      updateDotRing("days-ring", days, 30, accent);
      updateDotRing("hours-ring", hours, 24, accent);
      updateDotRing("minutes-ring", minutes, 60, accent);
      updateDotRing("seconds-ring", seconds, 60, accent);
    }, 1000);
  }

  // --- 2. FAQ Accordion ---
  const questions = document.querySelectorAll(".accordion-question");
  questions.forEach((question) => {
    question.addEventListener("click", () => {
      const answer = question.nextElementSibling;
      answer.classList.toggle("active");
    });
  });

  // --- 3. Feather Icons ---
  if (window.feather) {
    window.feather.replace();
  }
});