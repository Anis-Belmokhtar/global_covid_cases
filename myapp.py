from flask import Flask
import requests
from datetime import date
from cassandra.cluster import Cluster

cluster = Cluster(contact_points=['172.17.0.2'], port=9042)
session = cluster.connect()
app = Flask(__name__)


@app.route('/')
def home():
    return '<h1>This is the starting page. Enter a country name in the url to find number of cases for Covid19.</h1>'


def update_record_in_db(country_name, cases):
    today = date.today()
    session.execute(
        """Update countries.cases set cases={}, publish_date='{}' where name='{}'""".format(cases, today, country_name))


def retrieve_record_from_api(country_name):
    # GET latest record from external api, update record in DB.
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
    session.execute("""Delete from countries.cases where name='{}'""".format(country_name))


def retrieve_record_from_db(country_name):
    records = session.execute("""Select * from countries.cases where name = '{}'""".format(country_name))
    if records:
        return records[0]
    else:
        return None


@app.route('/<country_name>', methods=['GET'])
def get_case_by_country(country_name):
    current_date = date.today()
    retrieved_record = retrieve_record_from_db(country_name)
    if retrieved_record and retrieved_record.publish_date == current_date:
        return 'Successfully retrieved DB record: {}, {}'.format(retrieved_record.cases, retrieved_record.publish_date)
    else:
        api_record = retrieve_record_from_api(country_name)
        if api_record:
            update_record_in_db(country_name, api_record.get("cases"))
            return 'Successfully retrieved api record and saved to DB: {}, {}'.format(api_record.get("cases"),
                                                                                      api_record.get("publish_date"))
        else:
            return 'Unable to find record for {}'.format(country_name)


@app.route('/<country_name>', methods=['DELETE'])
def delete_country(country_name):
    retrieved_record = retrieve_record_from_db(country_name)
    if retrieved_record:
        delete_record_from_db(country_name)
        return 'Successfully deleted db record.'
    else:
        return 'Record not found.'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
