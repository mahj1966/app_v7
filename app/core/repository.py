from typing import Dict, Any
import json
from datetime import datetime
from app.core.database import Database
from loguru import logger

class AWSResourceRepository:
    def __init__(self, db: Database):
        self.db = db

    def clear_resources(self, account_id: str, region: str, argument_name: str, argument_value: str):
        """Clear existing resources for given parameters."""
        query = """
            DELETE FROM aws_resources_json 
            WHERE trim(account_id) = :account_id 
            AND trim(region) = :region 
            AND trim(argument_name) = :argument_name 
            AND trim(argument_value) = :argument_value
        """
        self.db.execute_query(query, {
            'account_id': account_id,
            'region': region,
            'argument_name': argument_name,
            'argument_value': argument_value
        })

    def save_resource(self, 
                     account_id: str, 
                     region: str, 
                     json_data: Dict[str, Any],
                     argument_name: str,
                     argument_value: str,
                     attributes: str,
                     res_id: str = None):
        """Save AWS resource data."""
        query = """
            INSERT INTO aws_resources_json (
                account_id, region, json_data, argument_name, 
                argument_value, attributes, res_id, creation_date
            ) VALUES (
                :account_id, :region, :json_data, :argument_name,
                :argument_value, :attributes, :res_id, :creation_date
            )
        """
        self.db.execute_query(query, {
            'account_id': account_id,
            'region': region,
            'json_data': json.dumps(json_data, default=str),
            'argument_name': argument_name,
            'argument_value': argument_value,
            'attributes': attributes,
            'res_id': res_id,
            'creation_date': datetime.now()
        }) 