from flask import Flask, request, jsonify
import threading
import oracledb
import requests
import subprocess
import datetime
from jinja2 import Template
import logging
import os
import hcl2
import json
from functools import wraps
import time
import gitlab
import base64
import sys
from loguru import logger
import collections
import boto3
import uuid
from datetime import datetime
from ast import literal_eval
import random
import botocore
import base64
from datetime import date
from datetime import timedelta

app = Flask(__name__)
# Configure logging
logging.basicConfig(filename='discover_ec2_app.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
#######################
CHARSET = 'UTF-8'
#################################################
# execute sql statement COLLECT DATA RESOURCES
#################################################
resourceAccount = sys.argv[1]
resourceRegion = sys.argv[2]
resourceType = sys.argv[3]
resourceAtribute = sys.argv[4]
argument_name = sys.argv[5]
argument_value = sys.argv[6]
# Environment variables
GITLAB_URL = os.environ.get("GITLAB_URL", "https://gitlab.com")
API_KEY = os.environ.get("API_KEY", "default_api_key")  # Set yourAPI key

# Decorator for API key authentication
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_api_key = API_KEY
        if api_key and api_key == expected_api_key:
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized access"}), 401
    return decorated

# Database connection function
def get_db_connection():
    dsn = oracledb.makedsn(
        os.environ.get("ORACLE_HOST", "localhost"),
        os.environ.get("ORACLE_PORT", "1521"),
        service_name=os.environ.get("ORACLE_SERVICE_NAME", "orcl")
    )
    return oracledb.connect(
        user=os.environ.get("ORACLE_USER", "default_user"),
        password=os.environ.get("ORACLE_PASSWORD", "default_password"),
        dsn=dsn
    )

# Fetch functions for different data required for Terraform configuration
def fetch_data(conn, query, params):
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        result = cursor.fetchone()
        if not result:
            return None
        column_names = [col[0].lower() for col in cursor.description]
        return dict(zip(column_names, result))
    except oracledb.DatabaseError as e:
        logging.error(f"Database error fetching data: {e}")
        raise

def fetchall_data(conn, query, params):
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
        if not results:
            return []
        column_names = [col[0].lower() for col in cursor.description]
        return [dict(zip(column_names, row)) for row in results]
    except oracledb.DatabaseError as e:
        logging.error(f"Database error fetching all data: {e}")
        raise
    
# sql commit insert update  functions for different data
def sql_commit_data(conn, query, params):
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
    except oracledb.DatabaseError as e:
        logging.error(f"Database error fetching data: {e}")
        conn.rollback()
        raise

###################################################
### Discover EC2 ENI
###################################################
# Flask route to trigger the Terraform process via HTTP POST
@app.route('/api/discover_ec2_eni', methods=['POST'])
@require_api_key
def discover_ec2_eni():
    if resourceType == 'EC2_eni' :
        conn = get_db_connection()
        ec2_client = boto3.client('ec2',region_name=resourceRegion)
        ec2_instances = ec2_client.describe_network_interfaces()
        cursor = conn.cursor()
        cursor.execute("""
            delete aws_resources_json  where trim(account_id)= :resourceAccount and trim(region)=:resourceRegion and trim(argument_name)=:argument_name and trim(argument_value)=:argument_value
            """,[resourceAccount,resourceRegion,argument_name,argument_value])
        conn.commit()
        cursor = conn.cursor()
        cursor.execute("""
            insert into aws_resources_json(account_id,region,json_data,argument_name,argument_value,attributes,creation_date)
            values(:account,:region,:json_data,:argument_name,:argument_value,:attributes,:creation_date)
            """,[resourceAccount,resourceRegion,json.dumps(ec2_instances,default=str),argument_name,argument_value,resourceAtribute,datetime.now()])
        conn.commit()
###################################################
### Discover EC2 security_groups
###################################################
# Flask route to trigger the Terraform process via HTTP POST
@app.route('/api/discover_ec2_sg', methods=['POST'])
@require_api_key
def discover_ec2_sg():
    conn = get_db_connection()
    if resourceType == 'EC2_sg' :
        ec2_client = boto3.client('ec2',region_name=resourceRegion)
        ec2_instances = ec2_client.describe_security_groups()
        cursor = conn.cursor()
        cursor.execute("""
            delete aws_resources_json  where trim(account_id)= :resourceAccount and trim(region)=:resourceRegion and trim(argument_name)=:argument_name and trim(argument_value)=:argument_value
            """,[resourceAccount,resourceRegion,argument_name,argument_value])
        conn.commit()
        cursor = conn.cursor()
        cursor.execute("""
            insert into aws_resources_json(account_id,region,json_data,argument_name,argument_value,attributes,creation_date)'
                values(:account,:region,:json_data,:argument_name,:argument_value,:attributes,:creation_date)
            """,[resourceAccount,resourceRegion,json.dumps(ec2_instances,default=str),argument_name,argument_value,resourceAtribute,datetime.now()])
        conn.commit()
###################################################
### Insert EC2 Volume
###################################################
# Flask route to trigger the Terraform process via HTTP POST
@app.route('/api/discover_ec2_volumes', methods=['POST'])
@require_api_key
def discover_ec2_volumes():
    conn = get_db_connection()
    if resourceType == 'EC2_Volumes' :
        ec2_client = boto3.client('ec2',region_name=resourceRegion)
        ec2_instances = ec2_client.describe_volumes()
        cursor = conn.cursor()
        cursor.execute("""
                delete aws_resources_json  where trim(account_id)= :resourceAccount and trim(region)=:resourceRegion and trim(argument_name)=:argument_name and trim(argument_value)=:argument_value
            """,[resourceAccount,resourceRegion,argument_name,argument_value])
        conn.commit()
        cursor = conn.cursor()
        cursor.execute("""
                insert into aws_resources_json(account_id,region,json_data,argument_name,argument_value,attributes,creation_date) 
                values(:account,:region,:json_data,:argument_name,:argument_value,:attributes,:creation_date)
            """,[resourceAccount,resourceRegion,json.dumps(ec2_instances,default=str),argument_name,argument_value,resourceAtribute,datetime.now()])
        conn.commit()
####################################################
### Discover EC2
###################################################
# Flask route to trigger the Terraform process via HTTP POST
@app.route('/api/discover_ec2', methods=['POST'])
@require_api_key
def discover_ec2():
    conn = get_db_connection()
    if resourceType == 'EC2' :
        ec2_client = boto3.client('ec2',region_name=resourceRegion)
        paginator = ec2_client.get_paginator('describe_instances')
        ec2_instance = response['Reservations']
        response = paginator.paginate().build_full_result()
        cursor = conn.cursor()
        cursor.execute("""
                delete aws_resources_json  where trim(account_id)= :resourceAccount and trim(region)=:resourceRegion and trim(argument_name)=:argument_name and trim(argument_value)=:argument_value
            """,[resourceAccount,resourceRegion,argument_name,argument_value])
        conn.commit()
        for instance in ec2_instance:
            cursor = conn.cursor()
            cursor.execute("""
                insert into aws_resources_json(account_id,region,json_data,argument_name,argument_value,attributes,res_id,creation_date)
                values(:account,:region,:json_data,:argument_name,:argument_value,:attributes, :res_id,:creation_date)
                """,[resourceAccount,resourceRegion,json.dumps(instance['Instances'],default=str),argument_name,argument_value,resourceAtribute,str(instance['Instances'][0]['InstanceId']),datetime.now()])
            conn.commit()    
####################################################
### Insert EC2 TYPE
###################################################
# Flask route to trigger the Terraform process via HTTP POST
@app.route('/api/discover_ec2_type', methods=['POST'])
@require_api_key
def discover_ec2_type():
    conn = get_db_connection()
    if resourceType == 'EC2_type' :
        ec2_client = boto3.client('ec2',region_name=resourceRegion)
        paginator = ec2_client.get_paginator('describe_instance_types')
        response = paginator.paginate().build_full_result()
        ec2_instance = response['InstanceTypes']
        cursor = conn.cursor()
        cursor.execute("""
                delete aws_resources_json  where trim(account_id)= :resourceAccount and trim(region)=:resourceRegion and trim(argument_name)=:argument_name and trim(argument_value)=:argument_value
            """,[resourceAccount,resourceRegion,argument_name,argument_value])
        conn.commit()
        for instance in ec2_instance:
            cursor = conn.cursor()
            cursor.execute("""
                insert into aws_resources_json(account_id,region,json_data,argument_name,argument_value,attributes,creation_date)
                values(:account,:region,:json_data,:argument_name,:argument_value,:attributes,:creation_date)
                """,[resourceAccount,resourceRegion,json.dumps(instance['Instances'],default=str),argument_name,argument_value,resourceAtribute,str(instance['Instances'][0]['InstanceId']),datetime.now()])
            conn.commit()  

#################################################################################################
# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8443, debug=True)
