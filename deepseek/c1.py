from flask import Flask, request, jsonify
import oracledb
import boto3
import json
import os
import sys
from datetime import datetime
from functools import wraps
from loguru import logger
from typing import Dict, List, Optional

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logger.add("discover_ec2_app.log", rotation="10 MB", level="INFO")

# Constants
CHARSET = 'UTF-8'
GITLAB_URL = os.environ.get("GITLAB_URL", "https://gitlab.com")
API_KEY = os.environ.get("API_KEY", "default_api_key")  # Set your API key

# Command-line arguments
resource_account = sys.argv[1]
resource_region = sys.argv[2]
resource_type = sys.argv[3]
resource_attribute = sys.argv[4]
argument_name = sys.argv[5]
argument_value = sys.argv[6]


# Decorator for API key authentication
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key and api_key == API_KEY:
            return f(*args, **kwargs)
        else:
            logger.warning(f"Unauthorized access attempt with API key: {api_key}")
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


# Generic function to execute SQL queries
def execute_query(conn, query: str, params: Dict, fetch_one: bool = False):
    with conn.cursor() as cursor:
        try:
            cursor.execute(query, params)
            if fetch_one:
                result = cursor.fetchone()
                if not result:
                    return None
                column_names = [col[0].lower() for col in cursor.description]
                return dict(zip(column_names, result))
            else:
                results = cursor.fetchall()
                if not results:
                    return []
                column_names = [col[0].lower() for col in cursor.description]
                return [dict(zip(column_names, row)) for row in results]
        except oracledb.DatabaseError as e:
            logger.error(f"Database error: {e}")
            raise


# Generic function to insert/update data
def commit_data(conn, query: str, params: Dict):
    with conn.cursor() as cursor:
        try:
            cursor.execute(query, params)
            conn.commit()
        except oracledb.DatabaseError as e:
            logger.error(f"Database error: {e}")
            conn.rollback()
            raise


# Generic function to fetch AWS resources
def fetch_aws_resources(service: str, region: str, action: str, **kwargs):
    client = boto3.client(service, region_name=region)
    paginator = client.get_paginator(action)
    return paginator.paginate(**kwargs).build_full_result()


# Flask route to discover EC2 resources
@app.route('/api/discover_ec2', methods=['POST'])
@require_api_key
def discover_ec2():
    if resource_type == 'EC2':
        conn = get_db_connection()
        try:
            response = fetch_aws_resources('ec2', resource_region, 'describe_instances')
            ec2_instances = response['Reservations']

            # Delete existing records
            commit_data(conn, """
                DELETE FROM aws_resources_json 
                WHERE TRIM(account_id) = :account AND TRIM(region) = :region 
                AND TRIM(argument_name) = :arg_name AND TRIM(argument_value) = :arg_value
            """, {"account": resource_account, "region": resource_region, "arg_name": argument_name, "arg_value": argument_value})

            # Insert new records
            for instance in ec2_instances:
                commit_data(conn, """
                    INSERT INTO aws_resources_json(account_id, region, json_data, argument_name, argument_value, attributes, res_id, creation_date)
                    VALUES (:account, :region, :json_data, :arg_name, :arg_value, :attributes, :res_id, :creation_date)
                """, {
                    "account": resource_account,
                    "region": resource_region,
                    "json_data": json.dumps(instance['Instances'], default=str),
                    "arg_name": argument_name,
                    "arg_value": argument_value,
                    "attributes": resource_attribute,
                    "res_id": instance['Instances'][0]['InstanceId'],
                    "creation_date": datetime.now()
                })

            return jsonify({"message": "EC2 instances discovered and saved successfully"}), 200

        except Exception as e:
            logger.error(f"Error discovering EC2 instances: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            conn.close()
    else:
        return jsonify({"error": "Invalid resource type"}), 400


# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8443, debug=True)
