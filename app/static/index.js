document.addEventListener("DOMContentLoaded", function() {
    setTimeout(() => {
        const msgs = document.getElementsByClassName("messages");
        for (let i = 0; i < msgs.length; i++) {
            msgs[i].style.display = "none";
        }
    }, 3000);

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

    const rating = document.getElementById("comment-form");
    if (rating) {
        rating.addEventListener("submit", function(event) {
            const selected = document.querySelector('input[name="rating"]:checked');
            if (!selected) {
                event.preventDefault();
                alert("Please Select rating");
            }
        });
    }

    const ratingUpdate = document.getElementById("comment-update-form");
    if (ratingUpdate) {
        ratingUpdate.addEventListener("submit", function(event) {
            const selected = document.querySelector('input[name="rating"]:checked');
            if (!selected) {
                event.preventDefault();
                alert("Please Select rating");
            }
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

    const del = document.getElementById("delete-user");
    if (del) {
        del.addEventListener("click", function(event) {
            const confirmed = confirm("THIS ACTION CANNOT BE UNDONE!");
            if (!confirmed) {
                event.preventDefault();
                console.log("Delete action canceled.");
            }
        });
    }

    const user = document.getElementById("user")
    if (user) {
        user.addEventListener("click", function() {
            const umenu = document.getElementById("umenu");
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

    const report = document.getElementById("report-select")
    if (report) {
        report.addEventListener("change", function() {
            text = document.getElementById("other-div")
            textbox = document.getElementById("other-report")
            pop = document.getElementById("popup")
            scam = document.getElementById("scam-div")
            scampid = document.getElementById("scam-product")

            if (report.value === "Other") {
                text.style.display = "block"
                pop.classList.remove("h150");
                pop.classList.add("h300");
            } else {
                text.style.display = "none"
                pop.style.height = 150
                pop.classList.remove("h300");
                pop.classList.add("h150");
                textbox.removeAttribute("required", "")
            }

            if (report.value === "Scam") {
                scam.style.display = "block"
                scampid.setAttribute("required", "required")
            } else {
                scam.style.display = "none"
                scampid.removeAttribute("required", "")
            }
        });
    }

    if (!window.location.href.includes("/user/")) {
        multiform("searchbar", "searchfilter")
        multiform("searchfilter", "searchbar")
    }
});

function multiform(form1, form2) {
    document.getElementById(form1).addEventListener("submit", function(event) {
        event.preventDefault();
        const filter = document.getElementById(form2);

        const formData = new FormData(this);
        const filterData = new FormData(filter);
        filterData.forEach((value, key) => formData.append(key, value));

        const query = new URLSearchParams(formData).toString();
        window.location.href = this.action + '?' + query;
    })
}
