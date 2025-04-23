document.addEventListener("DOMContentLoaded", function() {
    const add = document.getElementById("add-comment");
    if (add) {
        add.addEventListener('click', function() {
            let c = document.getElementById("comment-form");
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

    const update = document.getElementById("update-comment");
    if (update) {
        update.addEventListener('click', function() {
            let c = document.getElementById("comment-update-form");
            let comment = document.getElementById("user-comment");
            if (c.style.display === "block") {
                c.style.display = "none";
                comment.style.display = "block";
            } else {
                comment.style.display = "none";
                c.style.display = "block";
            }
        });
    }

    const cancelUpdate = document.getElementById("cancel-update");
    if (cancelUpdate) {
        cancelUpdate.addEventListener("click", function() {
            document.getElementById("comment-update-form").style.display = "none";
            document.getElementById("user-comment").style.display = "block";
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

    user = document.getElementById("user")
    if (user) {
        user.addEventListener("click", function() {
            umenu = document.getElementById("umenu");
            if (umenu.style.display === "none" || umenu.style.display === '') {
                umenu.style.display = "flex";
            } else {
                umenu.style.display = "none";
            }
        });

        document.addEventListener('click', function(event) {
            if (umenu.style.display === 'flex' && !user.contains(event.target) && !umenu.contains(event.target)) {
                umenu.style.display = 'none';
            }
        });
    }
});
