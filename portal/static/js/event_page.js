document.addEventListener("DOMContentLoaded", function () {
    const accentColor = getComputedStyle(document.documentElement).getPropertyValue('--accent');

    // --- 1. SVG Ring Functions ---
    function setupDotRing(svgId, dots, color) {
      const svg = document.getElementById(svgId);
      if (!svg) return;
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
        circle.setAttribute("fill", "#333"); // Default dot color
        circle.setAttribute("class", "dot");
        svg.appendChild(circle);
      }
    }

    function updateDotRing(svgId, value, max, accent) {
      const svg = document.getElementById(svgId);
      if (!svg) return;
      const dots = svg.querySelectorAll(".dot");
      const litDots = (value / max) * dots.length;
      for (let i = 0; i < dots.length; i++) {
        dots[i].setAttribute("fill", i < litDots ? accent : "#333");
      }
    }

    // --- 2. Phased Countdown & Button Logic ---
    const countdownSection = document.getElementById("countdown-section");

    if (countdownSection) {
      // Setup rings
      // Using 60 dots for all rings makes the 'max' mapping easier
      setupDotRing("days-ring", 60, accentColor);
      setupDotRing("hours-ring", 60, accentColor);
      setupDotRing("minutes-ring", 60, accentColor);
      setupDotRing("seconds-ring", 60, accentColor);

      // Get dates from data attributes
      const regEndDate = new Date(
        countdownSection.dataset.regEnd
      ).getTime();
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
      const countdownEl = document.getElementById("countdown");

      const countdownInterval = setInterval(function () {
        const now = new Date().getTime();
        let targetDate, targetTitle;
        let maxDays = 30; // Default max days for ring display

        // --- This is the core logic ---
        if (now < regEndDate) {
          targetDate = regEndDate;
          targetTitle = "Registration Closes In:";
          maxDays = Math.max(
            30,
            Math.floor((regEndDate - now) / (1000 * 60 * 60 * 24))
          );
          if (buttonEl) {
            buttonEl.disabled = false;
            buttonEl.textContent = "Register Now";
            buttonEl.style.opacity = 1;
            buttonEl.style.cursor = "pointer";
          }
        } else if (now < eventStartDate) {
          targetDate = eventStartDate;
          targetTitle = "Event Starts In:";
          maxDays = Math.max(
            7,
            Math.floor((eventStartDate - now) / (1000 * 60 * 60 * 24))
          );
          if (buttonEl) {
            buttonEl.disabled = true;
            buttonEl.textContent = "Registration Closed";
            buttonEl.style.opacity = 0.6;
            buttonEl.style.cursor = "not-allowed";
          }
        } else if (now < revealTimeDate) {
          targetDate = revealTimeDate;
          targetTitle = "Problem Statements Reveal In:";
          maxDays = Math.max(
            1,
            Math.floor((revealTimeDate - now) / (1000 * 60 * 60 * 24))
          );
        } else {
          // Event is live or over
          titleEl.textContent = "The Event is Live!";
          if(countdownEl) countdownEl.style.display = "none";
          clearInterval(countdownInterval);
          return;
        }

        // Update title
        if(titleEl) titleEl.textContent = targetTitle;

        // Calculate distance
        const distance = targetDate - now;

        // Calculate time units
        let days = Math.floor(distance / (1000 * 60 * 60 * 24));
        let hours = Math.floor(
          (distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
        );
        let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        let seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Update text
        if(daysEl) daysEl.textContent = days;
        if(hoursEl) hoursEl.textContent = hours;
        if(minutesEl) minutesEl.textContent = minutes;
        if(secondsEl) secondsEl.textContent = seconds;

        // Update SVG Dot Rings
        updateDotRing("days-ring", days, maxDays, accentColor); // Use dynamic max
        updateDotRing("hours-ring", hours, 24, accentColor);
        updateDotRing("minutes-ring", minutes, 60, accentColor);
        updateDotRing("seconds-ring", seconds, 60, accentColor);
      }, 1000);
    }

    // --- 3. FAQ Accordion ---
    document.querySelectorAll(".accordion-question").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const answer = this.nextElementSibling;
        const isHidden = answer.classList.contains("hidden");

        // Optional: Close all other answers
        // document.querySelectorAll(".accordion-answer").forEach(function(ans) {
        //   ans.classList.add("hidden");
        // });
        
        // Toggle the clicked answer
        if (isHidden) {
          answer.classList.remove("hidden");
        } else {
          answer.classList.add("hidden");
        }
      });
    });

    // --- 4. Feather Icons ---
    if (window.feather) {
      window.feather.replace();
    }
  });
