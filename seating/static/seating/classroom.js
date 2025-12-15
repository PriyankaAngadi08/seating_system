document.querySelectorAll(".seat").forEach(seat => {
    seat.addEventListener("mouseenter", () => {
        seat.style.transform = "scale(1.05)";
    });
    seat.addEventListener("mouseleave", () => {
        seat.style.transform = "scale(1)";
    });
});
