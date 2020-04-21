from flask import Flask
import requests
from datetime import date
from cassandra.cluster import Cluster

cluster = Cluster(contact_points=['172.17.0.2'], port=9042)
session = cluster.connect()
app = Flask(__name__)


@app.route('/')
def home():
    return '<h1>This is the starting page. Enter a country name in the url to find number of cases for Covid19.</h1>', 200


def update_record_in_db(country_name, cases):
    # Updates the DB with a record for the given country using the given cases, setting the date to 'today'. If the
    # record is present, it will overwrite. If not, it will create a new record.
    today = date.today()
    session.execute(
        """Update countries.cases set cases={}, publish_date='{}' where name='{}'""".format(cases, today, country_name))


def retrieve_record_from_api(country_name):
    # Retrieves the record from the external api for the given country. Returns a Python dictionary containing the
    # number of cases (from the api), today's date and the given country name. Returns none if the api can't process
    # the given country name.
    covid_url = 'https://api.covid19api.com/total/country/{country}/status/confirmed'.format(country=country_name)
    resp = requests.get(covid_url)
    if resp.ok:
        api_records = resp.json()
        latest_api_record = api_records[-1]
        cases = latest_api_record["Cases"]
        return {"cases": cases, "publish_date": date.today(), "country_name": country_name}
    else:
        return None


def delete_record_from_db(country_name):
    # Simply sends a DB command to delete the matching record from the DB.
    session.execute("""Delete from countries.cases where name='{}'""".format(country_name))


def retrieve_record_from_db(country_name):
    # Retrieves the record from the DB and returns the row with all its attributes accessible. Returns none if the
    # record doesn't exist in the DB.
    records = session.execute("""Select * from countries.cases where name = '{}'""".format(country_name))
    if records:
        return records[0]
    else:
        return None


@app.route('/<country_name>', methods=['GET'])
def get_case_by_country(country_name):
    # Calls method to retrieve a record from the DB. If the record exists and is up-to-date (by comparing with
    # current_date), returns the number of cases to the user. If either conditions fail, calls method to make an
    # external api address, update the DB and return the cases.
    current_date = date.today()
    retrieved_record = retrieve_record_from_db(country_name)
    if retrieved_record and retrieved_record.publish_date == current_date:
        return 'Successfully retrieved DB record: {} cases, as of {}'.format(retrieved_record.cases,
                                                                             retrieved_record.publish_date), 200
    else:
        api_record = retrieve_record_from_api(country_name)
        if api_record:
            update_record_in_db(country_name, api_record.get("cases"))
            return 'Successfully retrieved api record and saved to DB: {} cases, as of {}'.format(
                api_record.get("cases"),
                api_record.get("publish_date")), 200
        else:
            return 'Unable to find record for {}'.format(country_name), 400


@app.route('/<country_name>', methods=['DELETE'])
def delete_country(country_name):
    # Calls method to retrieve record from DB. If found, calls the delete method. If not, returns 'Record not found.'
    retrieved_record = retrieve_record_from_db(country_name)
    if retrieved_record:
        delete_record_from_db(country_name)
        return 'Successfully deleted db record.', 200
    else:
        return 'Record not found.', 404


if __name__ == '__main__':
    app.run(host='0.0.0.0')
