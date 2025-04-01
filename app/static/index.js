document.addEventListener("DOMContentLoaded", function() {
    const add = document.getElementById("add-comment");

    if (add) {
        add.addEventListener('click', function() {
            var c = document.getElementById("comment-form");
            if (c.style.display === "none" || c.style.display === '') {
                c.style.display = "block";
            } else {
                c.style.display = "none";
            }
        });
    }

    const cancel = document.getElementById("cancel");
    if (cancel) {
        cancel.addEventListener("click", function() {
            document.getElementById("comment-form").style.display = "none";
        });
    }

    const links = document.querySelectorAll(".confirm");
    links.forEach(link => {
        link.addEventListener("click", function(event) {
            const confirmed = confirm("Are you sure?");
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
});
