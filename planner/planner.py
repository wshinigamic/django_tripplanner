import haversine
import pandas as pd
import math
import sets
import time
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

class CreateDistanceCallback(object):
    def __init__(self, locations, no_depot = True):
        num_locations = len(locations)
        if no_depot == True:
            depot = num_locations - 1   # Dummy node for arbitrary start and end location
        else:
            depot = -1
        self.matrix = {}

        for from_node in xrange(num_locations):
            self.matrix[from_node] = {}
            for to_node in xrange(num_locations):
                if from_node == depot or to_node == depot:
                    self.matrix[from_node][to_node] = 0
                else:
                    lat1 = locations[from_node][0]
                    lon1 = locations[from_node][1]
                    lat2 = locations[to_node][0]
                    lon2 = locations[to_node][1]
                    self.matrix[from_node][to_node] = \
                        haversine.haversine(lat1, lon1, lat2, lon2)
            
    def Distance(self, from_node, to_node):
        return self.matrix[from_node][to_node]
    

class CreateVisitDurationCallback(object):
    def __init__(self, visit_durations):
        self.matrix = visit_durations

    def VisitDuration(self, from_node, to_node):
        return self.matrix[from_node]


class CreateTravelTimeCallback(object):
    def __init__(self, dist_callback, speed):
        self.dist_callback = dist_callback
        self.speed = speed

    def TravelTime(self, from_node, to_node):
        travel_time = self.dist_callback(from_node, to_node) / self.speed
        travel_time = math.ceil(travel_time/15.0)*15    # Round up to nearest 15 minutes
        return travel_time


class CreateTotalTimeCallback(object):
    def __init__(self, visit_time_callback, travel_time_callback):
        self.visit_time_callback = visit_time_callback
        self.travel_time_callback = travel_time_callback

    def TotalTime(self, from_node, to_node):
        visit_time = self.visit_time_callback(from_node, to_node)
        travel_time = self.travel_time_callback(from_node, to_node)
        return visit_time + travel_time


def main(num_loc, df, num_days = 3, start_coords = [], end_coords = [],
         visit_coord = None, start_day = 0, start_time = 10*60,
         end_time = 20*60, lunch_time = 720, lunch_duration = 60,
         dinner_time = 1020, dinner_duration = 60):
    assert num_loc > 0
    
    # Create data
    if len(start_coords) > 0:
        data = create_data_array(num_loc, df, start_coords = start_coords,
                                 end_coords = end_coords)
    else:
        data = create_data_array(num_loc, df, visit_coord = visit_coord)
        
    locations = data[0]
    visit_durations = data[1]
    start_times = data[2]
    end_times = data[3]
    closed_days = data[4]
    attractions = data[5]
    address = data[6]
    reviews_summary = data[7]
    about = data[8]
    no_depot = True

    if len(locations) != num_loc + 2*num_days:
        return None

    if len(start_coords) > 0:
        for i in range(len(start_coords)):
            visit_durations.append(start_time)
            start_times.append(0)
            end_times.append(24*60)
        no_depot = False
        start_index = range(num_loc, num_loc + num_days)
        end_index = range(num_loc + num_days, num_loc + 2*num_days)
        routing = pywrapcp.RoutingModel(len(locations), num_days,
                                        start_index, end_index)

    else:
        visit_durations.append(start_time)
        start_times.append(0)
        end_times.append(24*60)
        depot = len(locations) - 1
        routing = pywrapcp.RoutingModel(len(locations), num_days, depot)
    
    # Convert closed_days into a list such that j in list[i] iff j is closed
    # on day i
    closed_days_procd = [[] for _ in range(7)]
    for i in range(len(closed_days)):
        for j in closed_days[i]:
            closed_days_procd[j].append(i)

    search_parameters = pywrapcp.RoutingModel_DefaultSearchParameters()
    search_parameters.time_limit_ms = 10000

    dist_between_locations = CreateDistanceCallback(locations, no_depot)
    dist_callback = dist_between_locations.Distance
    
    routing.SetArcCostEvaluatorOfAllVehicles(dist_callback)

    horizon = end_time
    time = "Time"
    speed = 0.135

    visit_times = CreateVisitDurationCallback(visit_durations)
    visit_time_callback = visit_times.VisitDuration

    travel_times = CreateTravelTimeCallback(dist_callback, speed)
    travel_time_callback = travel_times.TravelTime

    total_times = CreateTotalTimeCallback(visit_time_callback, travel_time_callback)
    total_time_callback = total_times.TotalTime

    fix_start_cumul_to_zero = True

    routing.AddDimension(total_time_callback, horizon, horizon,
                         fix_start_cumul_to_zero, time)

    time_dimension = routing.GetDimensionOrDie(time)
    for location in range(num_loc):
        start = start_times[location]
        end = end_times[location]
        time_dimension.CumulVar(location).SetRange(start, end)

    # Add lunch and dinner breaks
    solver = routing.solver()
    for day in range(num_days):
        breaks = []
        lunch = solver.FixedDurationIntervalVar(lunch_time,
            lunch_time, lunch_duration, False, "Lunch" + str(day))
        dinner = solver.FixedDurationIntervalVar(dinner_time,
            dinner_time, dinner_duration, False, "Dinner" + str(day))
        breaks.append(lunch)
        breaks.append(dinner)
        time_dimension.SetBreakIntervalsOfVehicle(breaks, day)

    # Add attractions closed days as constraints
    for day in range(num_days):
        index = (day + start_day) % 7
        for attraction in closed_days_procd[index]:
            solver.AddConstraint(routing.VehicleVar(
                routing.NodeToIndex(attraction)) != day)
    
    assignment = routing.SolveWithParameters(search_parameters)
    
    if assignment:
        routes = []
        for day in range(num_days):
            index = routing.Start(day)
            node_index = routing.IndexToNode(index)
            route = []

            while not routing.IsEnd(index):
                node_index = routing.IndexToNode(index)
                index = assignment.Value(routing.NextVar(index))                
                route.append(node_index)
            
            routes.append(route[1:])

        print routes

        planned_attractions = []
        planned_durations = []
        planned_address = []
        planned_reviews_summary = []
        planned_travel_time = []
        planned_about = []
        for day in range(num_days):
            planned_attractions.append([attractions[i] for i in routes[day]])
            planned_durations.append([visit_durations[i] for i in routes[day]])
            planned_address.append([address[i] for i in routes[day]])
            planned_reviews_summary.append([reviews_summary[i] for i in routes[day]])
            planned_about.append([about[i] for i in routes[day]])
            trav_time = []
            for i in range(len(routes[day])):
                if i == 0:
                    if len(start_coords) > 0:
                        start_index = num_loc + day
                    else:
                        start_index = num_loc
                    end_index = routes[day][i]
                    trav_time.append(travel_time_callback(start_index, end_index))
                else:
                    start_index = routes[day][i]
                    end_index = routes[day][i-1]
                    trav_time.append(travel_time_callback(start_index, end_index))
            planned_travel_time.append(trav_time)

        output = [planned_attractions, planned_durations, planned_address,
                  planned_reviews_summary, planned_travel_time, lunch_time,
                  lunch_duration, dinner_time, dinner_duration, start_time,
                  planned_about]
        
        return output

    else:
        print "No solution found."
        return None


def create_data_array(num_loc, df, start_coords = [], end_coords = [],
                      visit_coord = None, min_radius = 9,
                      max_radius = 9*2):
    """
    -num_loc is the number of attractions to visit
    -df is the dataframe object, assumed to be preprocessed such that there are no
    nan fields for Coordinates and Suggested Duration
    -start_coords and end_coords are the hotel locations, which can be unspecified
    -visit_coord is the approximate place to visit, which should be specified if
    hotel locations are not
    -min_radius and max_radius sets the boundary for attractions to be included
    based on distance considerations
    
    returns [locations, visit_durations, start_times, end_times, closed_days,
            attraction, address, reviews_summary]
    -locations is a list of attractions coordinates
    -visit_durations is the list of the suggested durations of visit
    -start_times is the list of attractions opening time
    -end_times is the list of latest time to start visiting the attractions,
    computed by subtracting visit_duration from attracting closing time. If
    end_time < start_time, set visit_duration to be the difference between opening
    and closing time and set end_time = start_time
    -closed_days is the list of lists of days that the attractions should not be
    visited

    If an attraction have opening and closing hours that vary by days, set
    start_time and end_time according to the following 2 criteria:
    1. Of all opening and closing hours interval, use the longest opening and
    closing hours that overlap with all intervals, condition on this being > 0.75
    the longest interval. Set closed_days for all undefined days.
    2. Else, use the first longest opening and closing hours interval and set closed
    days appropriately.
    """

    locations = []
    durations = []
    start_times = []
    end_times = []
    closed_days_list = []
    about = []
    
    df_coords = df["Coordinates"].tolist()
    if len(start_coords) == 0 and visit_coord == None:
        print "Must either specify start and end_coords or visit_coord"
        return
    elif len(start_coords) > 0:
        search_coords_set = sets.Set()
        for start_coord, end_coord in zip(start_coords, end_coords):
            lat1, lon1 = start_coord
            lat2, lon2 = end_coord
            search_coords_set.add(((lat1 + lat2)/2.0, (lon1 + lon2)/2.0))

        # Find attractions with min_radius
        while True:
            flag = False
            for coord in search_coords_set:
                lat1, lon1 = coord
                for loc in df_coords:
                    lat2, lon2 = eval(loc)
                    if haversine.haversine(lat1, lon1, lat2, lon2) <= min_radius:
                        df_row = df.loc[df["Coordinates"] == loc]
                        duration, start, end, closed_days = get_hours_details(df_row)
                        if not (start == 0 and end == 0):
                            locations.append((lat2, lon2))
                            durations.append(duration)
                            start_times.append(start)
                            end_times.append(end)
                            closed_days_list.append(closed_days)
                            df_coords.remove(loc)
                            flag = True
                            break
                if len(locations) == num_loc:
                    break
            if flag == False or len(locations) == num_loc:
                break

        # Find attractions with max_radius if len(locations) < num_loc
        if len(locations) < num_loc:
            while True:
                flag = False
                for coord in search_coords_set:
                    lat1, lon1 = coord
                    for loc in df_coords:
                        lat2, lon2 = eval(loc)
                        if haversine.haversine(lat1, lon1, lat2, lon2) <= min_radius:
                            df_row = df.loc[df["Coordinates"] == loc]
                            duration, start, end, closed_days = get_hours_details(df_row)
                            if not (start == 0 and end == 0):
                                locations.append((lat2, lon2))
                                durations.append(duration)
                                start_times.append(start)
                                end_times.append(end)
                                closed_days_list.append(closed_days)
                                df_coords.remove(loc)
                                flag = True
                                break
                    if len(locations) == num_loc:
                        break
                if flag == False or len(locations) == num_loc:
                    break
                
        attractions = [
            df[df['Coordinates']==str(coord)]['Attraction'].reset_index(drop = True)[0]
            for coord in locations
            ]
        address = [
            df[df['Coordinates']==str(coord)]['Address'].reset_index(drop = True)[0]
            for coord in locations
            ]
        reviews_summary = [
            df[df['Coordinates']==str(coord)]['ReviewsSummary'].reset_index(drop = True)[0]
            for coord in locations
            ]
        about = [
            df[df['Coordinates']==str(coord)]['About'].reset_index(drop = True)[0]
            for coord in locations
            ]

        locations.extend(start_coords)
        locations.extend(end_coords)
                    
    elif visit_coord != None:

        # Find attractions with min_radius
        lat1, lon1 = visit_coord
        for loc in df_coords:
            lat2, lon2 = eval(loc)
            if haversine.haversine(lat1, lon1, lat2, lon2) <= min_radius:
                df_row = df.loc[df["Coordinates"] == loc]
                duration, start, end, closed_days = get_hours_details(df_row)
                if not (start == 0 and end == 0):
                    locations.append((lat2, lon2))
                    durations.append(duration)
                    start_times.append(start)
                    end_times.append(end)
                    closed_days_list.append(closed_days)
                    df_coords.remove(loc)
            if len(locations) == num_loc:
                break

        # Find attractions with max_radius if len(locations) < num_loc
        if len(locations) < num_loc:
            for loc in df_coords:
                lat2, lon2 = eval(loc)
                if haversine.haversine(lat1, lon1, lat2, lon2) <= max_radius:
                    df_row = df.loc[df["Coordinates"] == loc]
                    duration, start, end, closed_days = get_hours_details(df_row)
                    if not (start == 0 and end == 0):
                        locations.append((lat2, lon2))
                        durations.append(duration)
                        start_times.append(start)
                        end_times.append(end)
                        closed_days_list.append(closed_days)
                        df_coords.remove(loc)
                if len(locations) == num_loc:
                    break

        attractions = [
            df[df['Coordinates']==str(coord)]['Attraction'].reset_index(drop = True)[0]
            for coord in locations
            ]
        address = [
            df[df['Coordinates']==str(coord)]['Address'].reset_index(drop = True)[0]
            for coord in locations
            ]
        reviews_summary = [
            df[df['Coordinates']==str(coord)]['ReviewsSummary'].reset_index(drop = True)[0]
            for coord in locations
            ]
        about = [
            df[df['Coordinates']==str(coord)]['About'].reset_index(drop = True)[0]
            for coord in locations
            ]

        locations.append(visit_coord)
        
    data = [locations, durations, start_times, end_times, closed_days_list,
            attractions, address, reviews_summary, about]

    return data


def get_hours_details(df_row):
    """
    returns [visit_duration, start_time, end_time, closed_days]
    -visit_duration is the suggested duration of visit
    -start_time is the attraction opening time
    -end_time is the latest time to start visiting the attraction, computed by
    subtracting visit_duration from attracting closing time. If end_time < start_time,
    set visit_duration to be the difference between opening
    and closing time and set end_time = start_time
    -closed_days is the list of days that the attraction should not be
    visited

    If an attraction have opening and closing hours that vary by days, set
    start_time and end_time according to the following 2 criteria:
    1. Of all opening and closing hours interval, use the longest opening and
    closing hours that overlap with all intervals, condition on this being > 0.75
    the longest interval. Set closed_days for all undefined days.
    2. Else, use the first longest opening and closing hours interval and set closed
    days appropriately.
    """
    # df_row["i"][0] = start, end where i = 0, ..., 6 for Sunday, ..., Saturday
    assert len(df_row) == 1
    df_row = df_row.reset_index(drop = True)
    longest_interval, index = 0, []
    start_max = 0
    end_min = 60*24
    closed_days = []
    duration = int(df_row["Durations"][0])
    for i in range(7):
        if pd.isnull(df_row[str(i)][0]):
            closed_days.append(i)
        else:
            start, end = eval(df_row[str(i)][0])
            interval = end - start
            if interval > longest_interval:
                longest_interval, index = interval, [i]
            elif interval == longest_interval:
                index.append(i)                
            if start > start_max:
                start_max = start
            if end < end_min:
                end_min = end
    if len(closed_days) == 7:
        start_max = 0
        end_min = 0
        duration = 0
    elif (end_min - start_max) < 0.75*longest_interval:
        start_max, end_min = eval(df_row[str(index[0])][0])
        for i in range(7):
            if i not in index:
                closed_days.append(i)

    # Check if duration is > maximum overlapping interval and adjust duration down to
    # a minimum of 0.75*original duration
    if (end_min - start_max) < duration:
        if (end_min - start_max) < 0.75*duration:
            start_max = 0
            end_min = 0
            duration = 0
            closed_days = range(7)
        else:
            duration = end_min - start_max

    return [duration, start_max, end_min - duration, closed_days]
        
        
def get_schedule(data):
    """data = [planned_attractions, planned_durations, planned_address,
                planned_reviews_summary, planned_travel_time, lunch_time,
                lunch_duration, dinner_time, dinner_duration, start_time,
                about]"""
    # Unpack the data
    attractions = data[0]
    durations = data[1]
    address = data[2]
    reviews_summary = data[3]
    travel_time = data[4]
    lunch_time = data[5]
    lunch_duration = data[6]
    dinner_time = data[7]
    dinner_duration = data[8]
    start_time = data[9]
    about = data[10]
    num_days = len(attractions)

    events_list = []
    time_schedules = []
    for day in range(num_days):
        current_time = start_time
        events = []
        # schedule[i] is the start time of events[i] for i < len(attractions[day])
        # and is the the end time of events[j] where j = len(attractions[day])
        schedule = []    
        for i in range(len(attractions[day])):
            events.append('T')
            schedule.append(current_time)
            current_time += travel_time[day][i]
            
            events.append(attractions[day][i])
            schedule.append(current_time)
            current_time += durations[day][i]

        schedule.append(current_time)

        # Insert lunch time
        abs_diff = [abs(lunch_time - i)  for i in schedule]
        min_index = abs_diff.index(min(abs_diff))
        lunch = schedule[min_index]
        events.insert(min_index, 'Lunch')
        schedule.insert(min_index, lunch)
        schedule = schedule[0:min_index + 1] + \
                [i + lunch_duration for i in schedule[min_index + 1:]]

        # Insert dinner time
        abs_diff = [abs(dinner_time - i) for i in schedule]
        min_index = abs_diff.index(min(abs_diff))
        dinner = schedule[min_index]
        events.insert(min_index, 'Dinner')
        schedule.insert(min_index, dinner)
        schedule = schedule[0:min_index + 1] + \
                [i + dinner_duration for i in schedule[min_index + 1:]]

        events_list.append(events)
        time_schedules.append(schedule)

    return events_list, time_schedules
            

def readable_list(events_list, time_schedules,
                  planned_address, planned_reviews_summary, planned_about):
    schedule_trip = []
    for day in range(len(events_list)):
        schedule_day = [["Day " + str(day + 1)]]
        for i in range(len(events_list[day])):
            event = events_list[day][i]
            if event == 'T':
                pass
            elif event == 'Lunch' or event == 'Dinner':
                event_details = []
                event_details.append(event)
                begin = time_schedules[day][i]
                end = time_schedules[day][i + 1]
                begin_formatted = '{:02d}:{:02d}'.format(*divmod(int(begin), 60))
                end_formatted = '{:02d}:{:02d}'.format(*divmod(int(end), 60))
                time = "Time: " + begin_formatted + " - " + end_formatted
                event_details.append(time)
                schedule_day.append(event_details)
            else:
                event_details = []
                event_details.append(event)                
                begin = time_schedules[day][i]
                end = time_schedules[day][i + 1]
                begin_formatted = '{:02d}:{:02d}'.format(*divmod(int(begin), 60))
                end_formatted = '{:02d}:{:02d}'.format(*divmod(int(end), 60))
                time = "Time: " + begin_formatted + " - " + end_formatted
                event_details.append(time)
                address = "Address: " + planned_address[day].pop(0)
                event_details.append(address)
                about = "About: " + planned_about[day].pop(0)
                event_details.append(about)
                rev_summary = "Reviews Summary: " + planned_reviews_summary[day].pop(0)
                event_details.append(rev_summary)
                schedule_day.append(event_details)
        schedule_trip.append(schedule_day)
    return schedule_trip


def main_binary_search(df, num_days = 3, start_coords = [], end_coords = [],
         visit_coord = None, start_day = 0, start_time = 10*60,
         end_time = 20*60, lunch_time = 720, lunch_duration = 60,
         dinner_time = 1020, dinner_duration = 60):
    # Set default max number of attractions per day to be 6.
    time_available = 20
    max_num_loc = 6*num_days
    min_num_loc = num_days - 1
    best_output = None
    time_start = time.time()
    while max_num_loc != min_num_loc:
        if (time.time() - time_start) < time_available:
            num_loc = int(round((max_num_loc + min_num_loc)/2.0))
            output = main(num_loc, df, num_days, start_coords, end_coords, visit_coord,
                          start_day, start_time, end_time, lunch_time, lunch_duration,
                          dinner_time, dinner_duration)
            if output is not None:
                best_output = output
                min_num_loc = num_loc
            else:
                max_num_loc = num_loc - 1
        else:
            break
    return best_output


if __name__ == "__main__":
    path = "D:\Documents\Tripadvisor\Singapore\Singapore_procd2.csv"
    df = pd.read_csv(path)
    start_coords = [(1.351278, 103.712358)]*3
    end_coords = [(1.351278, 103.712358)]*3
    #main_binary_search(df, visit_coord = (1.352074, 103.819839), start_day = 2)

    main_binary_search(df, start_coords = start_coords, end_coords = end_coords )

                    
