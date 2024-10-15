document.getElementById("generate-btn").addEventListener("click", () => {
    const course1 = document.getElementById("course1").value;
    const section1 = document.getElementById("section1").value;
    const faculty1 = document.getElementById("faculty1").value;

    const course2 = document.getElementById("course2").value;
    const section2 = document.getElementById("section2").value;
    const faculty2 = document.getElementById("faculty2").value;

    const course3 = document.getElementById("course3").value;
    const section3 = document.getElementById("section3").value;
    const faculty3 = document.getElementById("faculty3").value;

    const course4 = document.getElementById("course4").value;
    const section4 = document.getElementById("section4").value;
    const faculty4 = document.getElementById("faculty4").value;

    const excludeEmptySeats = document.getElementById("exclude-empty-seats").checked;

    const courses = [
        { course: course1, section: section1, faculty: faculty1 },
        { course: course2, section: section2, faculty: faculty2 },
        { course: course3, section: section3, faculty: faculty3 },
        { course: course4, section: section4, faculty: faculty4 }
    ].filter(entry => entry.course); // Filter out entries with empty course fields

    // Display loading spinner
    showLoading();

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
    })
    .catch(err => {
        console.error("Error fetching schedules:", err);
        hideLoading();
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
            console.log(course.courseCode);
            console.log(day);
            console.log(time);

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
                table.rows[row].cells[col].innerHTML = course.courseDetails;  // Fill in course details
            }
        });
    });
}

// Show/hide loading spinner
function showLoading() {
    document.getElementById("loading").style.display = "block";
}

function hideLoading() {
    document.getElementById("loading").style.display = "none";
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
