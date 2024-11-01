from datetime import datetime

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


def filter(taken_courses, exclude_empty_seats=False): 
    courses_dict = {} # string: dict

    for i in taken_courses:
        course_code = i["course"][0:3].upper() + i["course"][3:]
        if course_code not in courses_dict: 
            courses_dict[course_code] = {"validCourseDetails": [], "filter": i}

    for c in data: 
        if ( c["courseCode"] in courses_dict): 
            if(exclude_empty_seats): # if seat is empty exclude section
                if(c["defaultSeatCapacity"] - c["totalFillupSeat"] <= 0):
                    continue
            
            if(courses_dict[c["courseCode"]]["filter"]["faculty"] != ''): #only keep prefered faculty
                if(c["empShortName"] != courses_dict[c["courseCode"]]["filter"]["faculty"].upper() ): 
                    continue
            
            if(courses_dict[c["courseCode"]]["filter"]["avoid"] != ''): 
                if(c["empShortName"] == courses_dict[c["courseCode"]]["filter"]["avoid"].upper() ): 
                    continue
            
            if (courses_dict[c["courseCode"]]["filter"]["section"] != ''): #only keep prefered section
                if(int(c["courseDetails"][-3:-1]) != int(courses_dict[c["courseCode"]]["filter"]["section"])): 
                    continue


            # take only preferred time
            if(courses_dict[c["courseCode"]]["filter"]["pref_time"] != ''): 

                c_time = parse_schedule(c["classSchedule"])
                # print(c_time)
                time_matched = False
                for time in c_time: 

                    # print("pref time: ", end="")
                    # print(courses_dict[c["courseCode"]]["filter"]["pref_time"])

                    if time[1] == courses_dict[c["courseCode"]]["filter"]["pref_time"]: 
                        time_matched = True

                if not time_matched: 
                    continue

                
            courses_dict[c["courseCode"]]["validCourseDetails"].append(c)

    all_course_details = []
    for i in courses_dict.keys(): 
        all_course_details.append(courses_dict[i]["validCourseDetails"])
    return all_course_details


def cartesian_product(*course_schedules): 
    
    result = [()]

    for c in course_schedules: 

        temp = []
        for x in result: 
            for y in c: 
                new_tuple = x + (y,)
                if not conflicts(new_tuple): 
                    temp.append(new_tuple)
        result = temp
    return result
  

# Main function to generate all non-conflicting schedules
def generate_all_schedules(taken_courses, exclude_empty_seats):
    # type of taken_courses = [{'course': 'CSE220', 'section': '5', 'faculty': 'ABS'}, {'course': 'CSE250', 'section': '1', 'faculty': ''}, {'course': 'CSE320', 'section': '2', 'faculty': ''}, {'course': 'ECO101', 'section': '3', 'faculty': ''}]

    valid_combinations = []

    all_schedules = filter(taken_courses, exclude_empty_seats=exclude_empty_seats)
    valid_combinations = cartesian_product(*all_schedules)


    # print(len(valid_combinations))
    # print(type(valid_combinations))
    # print(type(valid_combinations[0][0]))
    # print(f"Combinations: {len(valid_combinations)}")
        

    return valid_combinations
