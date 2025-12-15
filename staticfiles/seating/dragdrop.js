document.addEventListener("DOMContentLoaded", function () {

    let draggedRow = null;

    document.querySelectorAll("#seat-body tr.draggable").forEach(row => {

        row.addEventListener("dragstart", function () {
            draggedRow = this;
            this.style.opacity = "0.5";
        });

        row.addEventListener("dragover", function (e) {
            e.preventDefault();
        });

        row.addEventListener("drop", function () {
            if (draggedRow && draggedRow !== this) {
                let temp = this.innerHTML;
                this.innerHTML = draggedRow.innerHTML;
                draggedRow.innerHTML = temp;
            }
        });

        row.addEventListener("dragend", function () {
            this.style.opacity = "1";
        });

    });

});
