from flask import Flask, render_template, request, jsonify, Response
from schedule import generate_all_schedules  # Import the schedule generation script
# from test import test_gen
import json

app = Flask(__name__)

def generate_large_json(schedules):
    yield '['
    for i, schedule in enumerate(schedules):
        if i > 0:
            yield ','
        yield json.dumps(schedule)
    yield ']'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    data = request.get_json()
    courses = data.get('courses', [])
    exclude_empty_seats = data.get('excludeEmptySeats', False)

    print(courses)


    # Example of processing the courses, including preferred section and faculty
    # for course in courses:
    #     course_name = course['course']
    #     preferred_section = course.get('section')
    #     preferred_faculty = course.get('faculty')

    #     # You would use these inputs in your schedule generation logic
    #     print(f"Course: {course_name}, Preferred Section: {preferred_section}, Preferred Faculty: {preferred_faculty}")

    # Call your schedule generation function and ensure it returns a list of tuples
    
    schedules = generate_all_schedules(courses, exclude_empty_seats=exclude_empty_seats)

    return Response(generate_large_json(schedules), content_type='application/json')


if __name__ == '__main__':
    # app.run(debug=True)
    app.run()