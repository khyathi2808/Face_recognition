import os
from datetime import datetime

# Trackers
first_person_name = None
start_time = None
last_seen_time = None
doc_created = {}
violation_logged = set()
person_visible = False  # New tracker

def handle_violation(face_count, results, folder="violations"):
    global first_person_name, start_time, last_seen_time, person_visible

    if not os.path.exists(folder):
        os.makedirs(folder)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    found_person = False

    # Check recognized faces
    for name, match, distance, _ in results:
        if match and first_person_name is None:
            # First recognized face
            first_person_name = name
            start_time = timestamp
            last_seen_time = timestamp
            _create_person_txt(first_person_name, folder)
            found_person = True
            person_visible = True
        elif match and name == first_person_name:
            last_seen_time = timestamp
            found_person = True
            person_visible = True

    # If not found, then it's either no face, multiple faces, or unknown
    if first_person_name and not found_person:
        if face_count == 0:
            _write_violation(first_person_name, f"No face detected at {timestamp}", folder, "no_face")
        elif face_count > 1:
            _write_violation(first_person_name, f"Multiple faces detected at {timestamp}", folder, "multi_face")
        else:
            for name, match, distance, _ in results:
                if not match:
                    _write_violation(first_person_name, f"Unknown face detected at {timestamp} (distance={distance:.2f})", folder, "unknown_face")

        if person_visible:
            last_seen_time = timestamp  # Update last seen only when person disappears
            person_visible = False

def _create_person_txt(person_name, folder):
    # Create a filename with name + date
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(folder, f"{person_name}_{date_str}.txt")
    doc_created[person_name] = filename

    with open(filename, 'w') as f:
        f.write(f"Monitoring Report for {person_name}\n\n")
        f.write("Start Time: (to be filled)\n")
        f.write("End Time: (to be filled)\n")
        f.write("\nViolations:\n")

def _write_violation(person_name, text, folder, violation_type):
    filename = doc_created.get(person_name)
    if not filename:
        return

    key = (person_name, violation_type)
    if key in violation_logged:
        return  # Only allow one entry per type
    violation_logged.add(key)

    with open(filename, 'a') as f:
        f.write(f"- {text}\n")

def finalize_report():
    global first_person_name, start_time, last_seen_time

    if first_person_name:
        filename = doc_created.get(first_person_name)
        if filename and os.path.exists(filename):
            # Read current lines
            with open(filename, 'r') as f:
                lines = f.readlines()

            # Update Start Time and End Time
            new_lines = []
            for line in lines:
                if line.startswith("Start Time:"):
                    new_lines.append(f"Start Time: {start_time}\n")
                elif line.startswith("End Time:"):
                    new_lines.append(f"End Time: {last_seen_time}\n")
                else:
                    new_lines.append(line)

            # Write back updated lines
            with open(filename, 'w') as f:
                f.writelines(new_lines)
