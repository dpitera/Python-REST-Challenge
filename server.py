from flask import Flask, request, jsonify
import argparse
import sys
import MySQLdb
import csv
import io

#Web app
app = Flask(__name__)

def serialize_people_results(people):
    results = []
    for person in people:
        # Handle age is None case
        age = person[3]
        if age != None:
            age = int(person[3])
        # Assume id exists because the primary key is auto incremented
        payload = {"id": int(person[0]),
                   "first name": person[1],
                   "last name": person[2],
                   "age": age,
                   "github account": person[4],
                   "date of third grade graduation": person[5]}
        results.append(payload)
    return jsonify({"result": results, "status": 200})

def get_people():
    cursor = db.cursor()
    sql = "SELECT * FROM PERSON;"
    try:
        cursor.execute(sql)
        people = cursor.fetchall()
        return serialize_people_results(people)
    except Exception as e:
        print("Failed to retrieve people with error {}.".format(e))
        print("\n")
        return jsonify({"status": 500, "error": e})

def get_people_sorted_by_age():
    cursor = db.cursor()
    sql = "SELECT * FROM PERSON ORDER BY AGE;"
    try:
        cursor.execute(sql)
        people = cursor.fetchall()
        return serialize_people_results(people)
    except Exception as e:
        print("Failed to retrieve people with error {}.".format(e))
        print("\n")
        return jsonify({"status": 500, "error": e})

def get_ids_from_last_name(lastname):
    cursor = db.cursor()
    sql = """SELECT PERSON.ID FROM PERSON WHERE LAST_NAME = "{}";""".format(lastname)
    try:
        cursor.execute(sql)
        ids = cursor.fetchall()
        ids_to_return = []
        for id in ids:
            ids_to_return.append(int(id[0]))
        return jsonify({"result": ids_to_return, "status": 200})
    except Exception as e:
        print("Failed to retrieve people with error {}.".format(e))
        print("\n")
        return jsonify({"status": 500, "error": e})

def transform_req_data_into_input_file_format(data):
    data =  {k.lower(): v for k, v in data.items()}
    age = str(data.get("age", ""))
    id_tag = str(data.get("id", ""))
    first_name = str(data.get("first", ""))
    last_name = str(data.get("last", ""))
    github = str(data.get("githubacct", ""))
    grad = str(data.get("date of third grade graduation", ""))
    person = {"\xef\xbb\xbfID": id_tag,
              "Last": last_name,
              "Date of 3rd Grade Graduation": grad,
              "Age": age,
              "GithubAcct": github,
              "First": first_name}
    if (app.debug == True):
        print(person)
    return person


@app.route('/ping',methods=['GET'])
def pingServer():
    '''
    Ping request to make sure server is alive, return 'pong'
    '''
    return "pong"

@app.route('/people',methods=['GET'])
def getPeople():
    '''
    Return a standard JSON block of people in any order of format. Must be valid JSON
    '''
    return get_people()

@app.route('/people/age',methods=['GET'])
def sortPeopleByAge():
    '''
    Returns Json block containing a list of people sorted by age youngest to oldest
    '''
    return get_people_sorted_by_age()

@app.route('/ids/lastname/<lastname>',methods=['GET'])
def getIdsByLastName(lastname):
    '''
    Returns Json block of ids found for the given last name
    Using path params
    '''
    return get_ids_from_last_name(lastname)

@app.route('/people/person',methods=['POST'])
def createPerson():
    '''
    Create person using params passed in to the requests's JSON body. Then, return JSON representation of all people
    '''
    req_data = request.get_json(force=True)
    person = transform_req_data_into_input_file_format(req_data)
    result, err = create_person(person)
    if (result == False):
        return jsonify({"status": 500, "error": "failed to create person with error {}".format(err)})
    return get_people()

def create_person(person):
    if (app.debug == True):
        print("Person we are creating: {}".format(person))
        print("\n")
    cursor = db.cursor()
    # Handle age is null case
    age = person[map_sql_header_to_input["AGE"]]
    if age == '':
        age = "NULL"
    # Handle id is null case
    id_tag = person[map_sql_header_to_input["ID"]]
    if id_tag == '':
        id_tag = "NULL"

    # TODO Make the date an actual date format
    sql = """
        INSERT INTO PERSON (ID, FIRST_NAME, LAST_NAME, AGE, GITHUB_ACCOUNT, DATE_OF_THIRD_GRADE_GRADUATION)
        VALUES ({}, "{}", "{}", {}, "{}", "{}")""".format(id_tag,
                                                  person[map_sql_header_to_input["FIRST_NAME"]],
                                                  person[map_sql_header_to_input["LAST_NAME"]],
                                                  age,
                                                  person[map_sql_header_to_input["GITHUB_ACCOUNT"]],
                                                  person[map_sql_header_to_input["DATE_OF_THIRD_GRADE_GRADUATION"]])
    if (app.debug == True):
        print("SQL to create said person: {}".format(sql))
        print("\n")
    try:
        cursor.execute(sql)
        db.commit()
        return True, True # boolean return is for success for the POST /people/person endpoint
    except Exception as e:
        print("Failed to create person {} with error {}.".format(person, e))
        print("\n")
        # TODO Design and implement a strategy for failed loads from file, i.e. write to a queue to be loaded later
        # TODO Check if failed to load because this person already exists in the db (as indictaed by the primary key);
        #       If this is the case, update the existing record with the new data
        db.rollback()
        return False, e

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-d","--debug", help="Optional Debug Mode for stack traces", action="store_true")

    parser.add_argument("port", help="Optional port on which to run this server. Port must be available")

    parser.add_argument("file", help="File to import data from")
    args = parser.parse_args()

    # TODO Fix id header serialization oddity
    map_sql_header_to_input = {"ID": "\xef\xbb\xbfID",
                               "LAST_NAME": "Last",
                               "DATE_OF_THIRD_GRADE_GRADUATION": "Date of 3rd Grade Graduation",
                               "AGE": "Age",
                               "GITHUB_ACCOUNT": "GithubAcct",
                               "FIRST_NAME": "First"}

    # TODO Make mysql db initialization and setupo automatic
    db = MySQLdb.connect("localhost", "username", "password", "people")

    with open(args.file) as f:
        reader = csv.DictReader(f)
        for r in reader:
           create_person(r)

    app.debug=args.debug
    port = args.port
    app.run(host='0.0.0.0', port=port)

