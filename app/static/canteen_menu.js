document.addEventListener("DOMContentLoaded", () => {
    fetch("/api/canteen-data")
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById("canteen-container").innerHTML = "<p>Access Denied. Please log in.</p>";
                return;
            }
            populateCampusDropdown(data.catering_facilities);
            displayCanteenData(data.catering_facilities, data.menu_items);
        });
});

function populateCampusDropdown(cateringFacilities) {
    const campusSelect = document.getElementById("campus-select");
    campusSelect.innerHTML = "";

    let defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "Select a Campus";
    defaultOption.disabled = true;
    defaultOption.selected = true;
    campusSelect.appendChild(defaultOption);

    cateringFacilities.forEach(campus => {
        let option = document.createElement("option");
        option.value = campus.campus;
        option.textContent = campus.campus;
        campusSelect.appendChild(option);
    });

    campusSelect.addEventListener("change", () => {
        const selectedCampus = campusSelect.value;
        fetch("/api/canteen-data")
            .then(response => response.json())
            .then(data => {
                const campusFacilities = data.catering_facilities.filter(campus => campus.campus === selectedCampus);
                displayCanteenData(campusFacilities, data.menu_items);
            });
    });
}

function displayCanteenData(cateringFacilities, menuItems) {
    const container = document.getElementById("canteen-container");
    container.innerHTML = "";

    cateringFacilities.forEach(campus => {
        let campusSection = document.createElement("section");
        campusSection.classList.add("campus");
        campusSection.innerHTML = `<h2>${campus.campus} Campus</h2>`;

        campus.outlets.forEach(outlet => {
            let outletDiv = document.createElement("div");
            outletDiv.classList.add("outlet");
            outletDiv.innerHTML = `<h3>${outlet.name}</h3><p><strong>Opening Times:</strong></p>`;

            let timesList = document.createElement("ul");
            if (typeof outlet.opening_times === "string") {
                timesList.innerHTML = `<li>${outlet.opening_times}</li>`;
            } else {
                Object.entries(outlet.opening_times).forEach(([meal, time]) => {
                    let li = document.createElement("li");
                    li.textContent = `${meal}: ${time}`;
                    timesList.appendChild(li);
                });
            }
            outletDiv.appendChild(timesList);

            let menuTable = document.createElement("table");
            menuTable.innerHTML = `
                <tr>
                    <th>Meal Type</th>
                    <th>Item</th>
                    <th>Price (€)</th>
                    <th>Dietary</th>
                </tr>`;

            menuItems
                .filter(item => item.campus === campus.campus && item.outlet === outlet.name)
                .forEach(item => {
                    let row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${item.meal_type}</td>
                        <td>${item.item_name}</td>
                        <td>${item.price.toFixed(2)}</td>
                        <td>${item.dietary}</td>`;
                    menuTable.appendChild(row);
                });

            outletDiv.appendChild(menuTable);
            campusSection.appendChild(outletDiv);
        });

        container.appendChild(campusSection);
    });
}
