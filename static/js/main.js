document.getElementById("generate-btn").addEventListener("click", () => {
    const course1 = document.getElementById("course1").value;
    const section1 = document.getElementById("section1").value;
    const faculty1 = document.getElementById("faculty1").value;
    const avoid1 = document.getElementById("avoid1").value;
    const pref_time1 = document.getElementById("pref_time1").value;

    const course2 = document.getElementById("course2").value;
    const section2 = document.getElementById("section2").value;
    const faculty2 = document.getElementById("faculty2").value;
    const avoid2 = document.getElementById("avoid2").value;
    const pref_time2 = document.getElementById("pref_time2").value;

    const course3 = document.getElementById("course3").value;
    const section3 = document.getElementById("section3").value;
    const faculty3 = document.getElementById("faculty3").value;
    const avoid3 = document.getElementById("avoid3").value;
    const pref_time3 = document.getElementById("pref_time3").value;

    const course4 = document.getElementById("course4").value;
    const section4 = document.getElementById("section4").value;
    const faculty4 = document.getElementById("faculty4").value;
    const avoid4 = document.getElementById("avoid4").value;
    const pref_time4 = document.getElementById("pref_time4").value;

    const course5 = document.getElementById("course5").value;
    const section5 = document.getElementById("section5").value;
    const faculty5 = document.getElementById("faculty5").value;
    const avoid5 = document.getElementById("avoid5").value;
    const pref_time5 = document.getElementById("pref_time5").value;

    const excludeEmptySeats = document.getElementById("exclude-empty-seats").checked;

    const courses = [
        { course: course1, section: section1, faculty: faculty1, avoid: avoid1, pref_time: pref_time1 },
        { course: course2, section: section2, faculty: faculty2, avoid: avoid2, pref_time: pref_time2 },
        { course: course3, section: section3, faculty: faculty3, avoid: avoid3, pref_time: pref_time3 },
        { course: course4, section: section4, faculty: faculty4, avoid: avoid4, pref_time: pref_time4 },
        { course: course5, section: section5, faculty: faculty5, avoid: avoid5, pref_time: pref_time5 }
    ].filter(entry => entry.course); // Filter out entries with empty course fields

    // Display loading spinner
    showLoading();
    resetMessages();  // Reset any previous messages
    
    fetch('/generate_schedule', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ courses, excludeEmptySeats })
    })
    .then(response => {
        if (!response.ok) {  // Check if the status is not OK
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();  // Wait for the entire response to arrive
    })
    .then(data => {
        hideLoading();
        schedules = data;  // The response is a list of schedules
        currentIndex = 0;
        displaySchedule(currentIndex);  // Display the first schedule combination
        displayStatusMessage(`Generated ${schedules.length} schedule combinations!`);
        updateCombinationIndicator();  // Show current viewing combination
    })
    .catch(err => {
        console.error("Error fetching schedules:", err);
        hideLoading();
        displayErrorMessage("An error occurred while generating the schedule, try changing the fitlers");
    });
    
});

let schedules = [];
let currentIndex = 0;

// Function to display schedule
function displaySchedule(index) {
    const scheduleTuple = schedules[index];  // Tuple of 4 dictionaries
    const table = document.getElementById("schedule-table");

    // Clear previous schedule
    for (let row = 1; row < table.rows.length; row++) {
        for (let col = 1; col < table.rows[row].cells.length; col++) {
            table.rows[row].cells[col].innerHTML = '';
        }
    }

    // Fill table with the current schedule
    scheduleTuple.forEach(course => {
        const times = course.classLabSchedule.split(',');
        times.forEach(timeSlot => {
            const [day, time] = timeSlot.match(/[A-Za-z]+|\d{2}:\d{2} [APM]{2}-\d{2}:\d{2} [APM]{2}/g);
            
            // console.log(course.courseCode);
            // console.log(day);
            // console.log(time);

            // Determine the column based on the day
            let col = -1;
            if (day.startsWith("Su")) col = 1;
            if (day.startsWith("Mo")) col = 2;
            if (day.startsWith("Tu")) col = 3;
            if (day.startsWith("We")) col = 4;
            if (day.startsWith("Th")) col = 5;
            if (day.startsWith("Fr")) col = 6;
            if (day.startsWith("Sa")) col = 7;

            // Determine the row based on the time
            const timeslots = [
                "08:00 AM-09:20 AM", "09:30 AM-10:50 AM", "11:00 AM-12:20 PM",
                "12:30 PM-01:50 PM", "02:00 PM-03:20 PM", "03:30 PM-04:50 PM", "05:00 PM-06:20 PM"
            ];
            const row = timeslots.findIndex(slot => time.includes(slot)) + 1;
            console.log(row);

            if (row > 0 && col > 0) {
                // table.rows[row].cells[col].innerHTML = course.courseDetails;
                table.rows[row].cells[col].innerHTML = course.courseDetails.concat("-", course.empShortName);  // Fill in course details
            }
        });
    });

    updateCombinationIndicator();  // Update combination indicator
}

// Show/hide loading spinner
function showLoading() {
    document.getElementById("loading").style.display = "block";
}

function hideLoading() {
    document.getElementById("loading").style.display = "none";
}

// Reset message display
function resetMessages() {
    document.getElementById("status-message").textContent = "";
    document.getElementById("combination-number").textContent = "";  // Make sure this is empty initially
}

// Display status messages (e.g., number of combinations generated)
function displayStatusMessage(message) {
    const statusMessage = document.getElementById("status-message");
    statusMessage.textContent = message;
    statusMessage.style.color = "#2e2c2c";  // Neutral color for success messages
}

// Display error messages
function displayErrorMessage(message) {
    const statusMessage = document.getElementById("status-message");
    statusMessage.textContent = message;
    statusMessage.style.color = "red";  // Red color for error messages
}

// Button event listeners for cycling schedules
document.getElementById("previous-btn").addEventListener("click", () => {
    if (currentIndex > 0) {
        currentIndex--;
        displaySchedule(currentIndex);
    }
});

document.getElementById("next-btn").addEventListener("click", () => {
    if (currentIndex < schedules.length - 1) {
        currentIndex++;
        displaySchedule(currentIndex);
    }
});

// Prototype - function to download the table 

// function downloadTableAsImage() {
//     // Reference to the table element
//     var table = document.getElementById('schedule-table');

//     // Use html2canvas to capture the table as an image
//     html2canvas(table).then(function (canvas) {
//         // Create a link element
//         var link = document.createElement('a');
//         link.href = canvas.toDataURL(); // Get the image data as a URL (base64)
//         link.download = 'schedule.png';    // Set the download attribute to specify filename

//         // Trigger the download
//         link.click();
//     });
// }

// Update which combination is being viewed
function updateCombinationIndicator() {
    const combinationIndicator = document.getElementById("combination-number");
    
    if (schedules.length > 0) {
        combinationIndicator.textContent = `Viewing combination ${currentIndex + 1} of ${schedules.length}`;
    } else {
        combinationIndicator.textContent = "";  // Keep it empty if no schedules exist
    }
}
