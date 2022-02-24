import os.path as osp
import numpy as np
import heapq

MENTOR = False

def read_data(path):
    contributors = {}
    projects = []
    with open(path) as f:
        line = f.readline()       
        C, P = [int(v) for v in line.split()]
        # Contributors
        for i in range(C):
            name, N = f.readline().split()
            N = int(N)
            contributor_skills = set()
            for j in range(N):
                skill, Li = f.readline().split()
                contributor_skills.add((skill, int(Li)))
            contributors[name] = contributor_skills
        # Projects
        for i in range(P):
            name, Di, Si, Bi, Ri = f.readline().split()
            Di = int(Di)
            Si = int(Si)
            Bi = int(Bi)
            Ri = int(Ri)
            requirement_skills = []
            for j in range(Ri):
                skill, Lk = f.readline().split()
                requirement_skills.append((skill, int(Lk)))
            projects.append([name, Di, Si, Bi, requirement_skills])
    return contributors, projects

def write_results(input_path, scheduled_projects):
    output_path_base = osp.join("output", osp.basename(input_path))
    i = 0
    while True:
        output_path = "{}_{:03d}".format(output_path_base, i)
        if not osp.isfile(output_path):
            break
        i += 1
    print(output_path)
    with open(output_path, "w") as f:
        f.write("{:d}\n".format(len(scheduled_projects)))
        for name, contributors in scheduled_projects:
            f.write("{}\n".format(name))
            f.write("{}\n".format(" ".join(contributors)))


def estimate_score(contributors, projects, scheduled_projects):
    _, lengths = np.unique([p for p, _ in scheduled_projects])
    assert np.all(lengths == 1), "some projects are scheduled multiple times"

    projects_dict = { p[0]:p[1:] for p in projects }
    contributors_dict = { c[0]:c[1:] for c in contributors }
    busy_people = {}

    score = 0
    t = 0
    for project_name, current_contributors in scheduled_projects:
        time, _score, _deadline, required_skills = projects_dict[project_name]
        for c in current_contributors:
            assert not c in busy_people, "busy contributor can not be used"

        possible_persons_for_skill = 0
        # for skill, required_level in required_skills:
    

def work_heuristic(project, t=0):
    name, time, score, deadline, req = project 
    if t + time < deadline + score:
        return deadline + score - t - time
    else:
        return 0


def find_contributor_with_skill(needed_skill, needed_level, has_skills, busy_people, suggestion, t):
    for level in range(needed_level, 101):
        key = (needed_skill, level)
        if key in has_skills:
            possible = sorted(has_skills[key], key=lambda x: x[1])
            for person, _ in possible:
                if busy_people[person] <= t and person not in [s[0] for s in suggestion]:
                    return person, key
        
    return None, None
    

def run(contributors, projects):
    # projects.sort(key=work_heuristic)
    t = 0
    scheduled_projects = [] # [[project1, [contributor1, contributor2, ...]], [p2, [c1, c2, c3, ...]], ...]
    done_projects = set()
    busy_people = {} # Name: time
    has_skills = {} # skill+level: [name1, name2...]
    for name, skills in contributors.items():
        busy_people[name] = 0
        for skill in skills:
            key = (skill[0], skill[1])
            if not key in has_skills:
                has_skills[key] = set()
            has_skills[key].add((name, len(skills)))

    times_heap = []
    while True:
        projects.sort(key=lambda p: work_heuristic(p, t))
        for name, time, score, deadline, required_skills in projects:
            possible_mentors = {}
            current_mentors = set()
            
            if name in done_projects or t + time > deadline + score:
                continue
            suggestion = []
            for needed_skill, needed_level in required_skills:
                current_level = needed_level
                current_mentor = None
                if MENTOR:
                    if needed_skill in possible_mentors and possible_mentors[needed_skill]["level"] >= needed_level:
                        current_level = needed_level - 1
                        current_mentor = possible_mentors[needed_skill]["person"]
                person, skill_key = find_contributor_with_skill(needed_skill, current_level, has_skills, busy_people, suggestion, t)
                if person is not None:
                    suggestion.append((person, skill_key))
                if MENTOR:
                    if person is not None:
                        for (skill, level) in contributors[person]:
                            if not skill in possible_mentors or possible_mentors[skill]["level"] > level:
                                possible_mentors[skill] = {
                                    "person": person,
                                    "level": level
                                }
            if len(suggestion) == len(required_skills):
                scheduled_projects.append([name, [sugg[0] for sugg in suggestion]])
                done_projects.add(name)
                if t + time not in times_heap:
                    heapq.heappush(times_heap, t + time)
                for i, (person, skill_key) in enumerate(suggestion):
                    if MENTOR and person in current_mentors:
                        continue
                    busy_people[person] = t + time
                    if skill_key[1] <= required_skills[i][1]:
                        has_skills[skill_key].remove((person, len(contributors[person])))
                        upgraded_skill = (skill_key[0], skill_key[1] + 1)
                        if not upgraded_skill in has_skills:
                            has_skills[upgraded_skill] = set()
                        has_skills[upgraded_skill].add((person, len(contributors[person])))
                    
        if len(times_heap) == 0:
            # No running project, no more projects we can do
            break
        t = heapq.heappop(times_heap)
        print("time", t)
        if len(done_projects) == len(projects):
            break
        if t > 1000000:
            break

    return scheduled_projects



if __name__ == "__main__":
    import sys
    path = sys.argv[-1]
    contributors, projects = read_data(path)
    # print(contributors)
    # print(projects)

    planned_projects = run(contributors, projects)
    # example_scheduled_projects = [
    #     ["proj1", ["A", "B", "C", "D"]],
    #     ["proj2", ["A", "B", "C", "D"]],
    #     ["proj3", ["A", "B", "C", "D"]],
    # ]
    write_results(path, planned_projects)
