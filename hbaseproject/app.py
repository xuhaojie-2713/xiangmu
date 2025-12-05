#!/usr/bin/env python3
from flask import Flask, render_template, redirect
from utils.qurydata import *

app = Flask(__name__)
app.secret_key = "session_key"


@app.route("/index")
def index():
    secondTypename, secondTypecount = get_secondType()
    companyname, companyvalue = get_companysize()
    workyear = get_workyear_counts()
    education_counts = get_education()
    city_value, city_name = get_city()
    job_name, job_value = get_top_five_job()
    companysum = get_count_companies()
    companysize = get_company_size_sum()
    return render_template(
        "index.html",
        secondTypename=secondTypename,
        secondTypecount=secondTypecount,
        companyname=companyname,
        companyvalue=companyvalue,
        workyear=workyear,
        education=education_counts,
        city_name=city_name,
        city_value=city_value,
        job_name=job_name,
        job_value=job_value,
        companysize=companysize,
        companysum=companysum
    )




if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port='8890')
