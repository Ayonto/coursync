from datetime import datetime
import itertools

import requests
import json



def scrape_full_schedule(): 
    url = "https://usis-cdn.eniamza.com/usisdump.json" 
    req = requests.get(url)

    json_data = json.dumps(req.json(), indent = 2)
    data = json.loads(json_data)
    
    return data

data = scrape_full_schedule()

def time_conflict(time1, time2):
    """
    Helper function to determine if two time ranges overlap.
    Each time is in the format 'HH:MM AM/PM'.
    """
    fmt = '%I:%M %p'  # Format for parsing time (12-hour clock with AM/PM)
    
    # Convert start and end times into datetime objects
    start1, end1 = [datetime.strptime(t.strip(), fmt) for t in time1.split('-')]
    start2, end2 = [datetime.strptime(t.strip(), fmt) for t in time2.split('-')]
    
    # Check if the time intervals overlap
    return start1 < end2 and start2 < end1

def parse_schedule(classLabSchedule):
    """
    Parse the classLabSchedule string into a structured format.
    Example input: "Monday(08:00 AM-09:20 AM-07H-31C),Wednesday(08:00 AM-09:20 AM-07H-31C)"
    Output: A list of tuples (day, time_range)
    """
    schedule_list = classLabSchedule.split(',')
    
    for entry in schedule_list:
        day, time_range_with_room = entry.split('(')
        time_range_with_room = time_range_with_room.rstrip(')')
        
        # Extract only the time range (ignoring classroom number)
        time_range = '-'.join(time_range_with_room.split('-')[:2])
        
        # Return a (day, time_range) tuple
        yield (day.strip(), time_range.strip())

def conflicts(courses):
    """
    Given a tuple of courses, check if there are any timing conflicts in their classLabSchedule.
    Returns True if there is a conflict, otherwise False.
    """
    # Iterate through each course
    for i in range(len(courses)):
        course1 = courses[i]
        for schedule1 in parse_schedule(course1['classLabSchedule']):
            day1, time1 = schedule1
            
            # Compare course1's schedule with all subsequent courses
            for j in range(i + 1, len(courses)):
                course2 = courses[j]
                for schedule2 in parse_schedule(course2['classLabSchedule']):
                    day2, time2 = schedule2
                    
                    if day1 == day2:  # Only compare if the days match
                        if time_conflict(time1, time2):
                            return True  # Conflict found
    
    return False  # No conflicts found

def filter(course, exclude_empty_seats):
    course_code = course["course"][0:3].upper() + course["course"][3:]
    section = course["section"]
    faculty = course["faculty"]
    avoid = course["avoid"]
    valid_course_details = []


    for c in data:
        if(c["courseCode"] == course_code):
            if(exclude_empty_seats): # if seat is empty exclude section
                if(c["defaultSeatCapacity"] - c["totalFillupSeat"] <= 0):
                    continue
            if(faculty != ''): #only keep prefered faculty
                if(c["empShortName"] != faculty.upper()): 
                    continue
            
            if(avoid != ''): 
                if(c["empShortName"] == avoid.upper()): 
                    continue
            
            if (section != ''): #only keep prefered section
                if(int(c["courseDetails"][-3:-1]) != int(section)): 
                    continue
        
            valid_course_details.append(c)
    return valid_course_details
        

# Main function to generate all non-conflicting schedules
def generate_all_schedules(taken_courses, exclude_empty_seats):
    # type of taken_courses = [{'course': 'CSE220', 'section': '5', 'faculty': 'ABS'}, {'course': 'CSE250', 'section': '1', 'faculty': ''}, {'course': 'CSE320', 'section': '2', 'faculty': ''}, {'course': 'ECO101', 'section': '3', 'faculty': ''}]

    # Debugging
    # print(f"EXCLUDE EMPTY SEAT: {exclude_empty_seats}")
    # print("#######################################")
    # print(taken_courses)


    all_combinations = []

    if(len(taken_courses) == 5): 

        c1_schedules = filter(taken_courses[0], exclude_empty_seats)
        c2_schedules = filter(taken_courses[1], exclude_empty_seats)
        c3_schedules = filter(taken_courses[2], exclude_empty_seats)
        c4_schedules = filter(taken_courses[3], exclude_empty_seats)
        c5_schedules = filter(taken_courses[4], exclude_empty_seats)

        all_combinations = list(itertools.product(c1_schedules, c2_schedules, c3_schedules, c4_schedules, c5_schedules))
    
    if(len(taken_courses) == 4): 

        c1_schedules = filter(taken_courses[0], exclude_empty_seats)
        c2_schedules = filter(taken_courses[1], exclude_empty_seats)
        c3_schedules = filter(taken_courses[2], exclude_empty_seats)
        c4_schedules = filter(taken_courses[3], exclude_empty_seats)

        all_combinations = list(itertools.product(c1_schedules, c2_schedules, c3_schedules, c4_schedules))
            
    elif(len(taken_courses) == 3): 

        c1_schedules = filter(taken_courses[0], exclude_empty_seats)
        c2_schedules = filter(taken_courses[1], exclude_empty_seats)
        c3_schedules = filter(taken_courses[2], exclude_empty_seats)

        all_combinations = list(itertools.product(c1_schedules, c2_schedules, c3_schedules))

    elif(len(taken_courses) == 2): 
        c1_schedules = filter(taken_courses[0], exclude_empty_seats)
        c2_schedules = filter(taken_courses[1], exclude_empty_seats)

        all_combinations = list(itertools.product(c1_schedules, c2_schedules))

    elif(len(taken_courses) == 1): 
        c1_schedules = filter(taken_courses[0], exclude_empty_seats)

        all_combinations = list(itertools.product(c1_schedules))
        
    valid_combinations= []
    for combination in all_combinations: 
        if not conflicts(combination): valid_combinations.append(combination)

    print(f"Combinations: {len(valid_combinations)}")
    return valid_combinations
