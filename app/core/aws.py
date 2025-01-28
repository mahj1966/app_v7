from typing import Dict, Any, List
import boto3
from datetime import datetime
from loguru import logger

class AWSService:
    def __init__(self, region: str, account_id: str):
        self.region = region
        self.account_id = account_id
        self.ec2_client = boto3.client('ec2', region_name=region)

    def discover_network_interfaces(self) -> Dict[str, Any]:
        """Discover EC2 Network Interfaces."""
        try:
            return self.ec2_client.describe_network_interfaces()
        except Exception as e:
            logger.error(f"Error discovering network interfaces: {e}")
            raise

    def discover_security_groups(self) -> Dict[str, Any]:
        """Discover EC2 Security Groups."""
        try:
            return self.ec2_client.describe_security_groups()
        except Exception as e:
            logger.error(f"Error discovering security groups: {e}")
            raise

    def discover_volumes(self) -> Dict[str, Any]:
        """Discover EC2 Volumes."""
        try:
            return self.ec2_client.describe_volumes()
        except Exception as e:
            logger.error(f"Error discovering volumes: {e}")
            raise

    def discover_instances(self) -> List[Dict[str, Any]]:
        """Discover EC2 Instances."""
        try:
            paginator = self.ec2_client.get_paginator('describe_instances')
            response = paginator.paginate().build_full_result()
            return response['Reservations']
        except Exception as e:
            logger.error(f"Error discovering EC2 instances: {e}")
            raise

    def discover_instance_types(self) -> List[Dict[str, Any]]:
        """Discover EC2 Instance Types."""
        try:
            paginator = self.ec2_client.get_paginator('describe_instance_types')
            response = paginator.paginate().build_full_result()
            return response['InstanceTypes']
        except Exception as e:
            logger.error(f"Error discovering instance types: {e}")
            raise 