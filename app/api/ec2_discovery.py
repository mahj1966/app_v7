from flask import Blueprint, request, jsonify
from app.core.aws import AWSService
from app.core.repository import AWSResourceRepository
from app.core.database import db
from app.utils.auth import require_api_key
from loguru import logger

ec2_discovery_bp = Blueprint('ec2_discovery', __name__)

@ec2_discovery_bp.route('/api/discover_ec2_eni', methods=['POST'])
@require_api_key
def discover_ec2_eni():
    """Discover EC2 Network Interfaces."""
    try:
        # Get parameters from request args
        account_id = request.args.get('resourceAccount')
        region = request.args.get('resourceRegion')
        argument_name = request.args.get('argument_name')
        argument_value = request.args.get('argument_value')

        aws_service = AWSService(region, account_id)
        repository = AWSResourceRepository(db)

        # Discover ENIs
        eni_data = aws_service.discover_network_interfaces()

        # Save to database
        repository.clear_resources(account_id, region, argument_name, argument_value)
        repository.save_resource(
            account_id=account_id,
            region=region,
            json_data=eni_data,
            argument_name=argument_name,
            argument_value=argument_value,
            attributes='EC2_eni'
        )

        return jsonify({"message": "ENI discovery completed successfully"}), 200
    except Exception as e:
        logger.error(f"Error in ENI discovery: {e}")
        return jsonify({"error": str(e)}), 500

@ec2_discovery_bp.route('/api/discover_ec2_sg', methods=['POST'])
@require_api_key
def discover_ec2_sg():
    """Discover EC2 Security Groups."""
    try:
        account_id = request.args.get('resourceAccount')
        region = request.args.get('resourceRegion')
        argument_name = request.args.get('argument_name')
        argument_value = request.args.get('argument_value')

        aws_service = AWSService(region, account_id)
        repository = AWSResourceRepository(db)

        # Discover Security Groups
        sg_data = aws_service.discover_security_groups()

        # Save to database
        repository.clear_resources(account_id, region, argument_name, argument_value)
        repository.save_resource(
            account_id=account_id,
            region=region,
            json_data=sg_data,
            argument_name=argument_name,
            argument_value=argument_value,
            attributes='EC2_sg'
        )

        return jsonify({"message": "Security Group discovery completed successfully"}), 200
    except Exception as e:
        logger.error(f"Error in Security Group discovery: {e}")
        return jsonify({"error": str(e)}), 500

@ec2_discovery_bp.route('/api/discover_ec2_volumes', methods=['POST'])
@require_api_key
def discover_ec2_volumes():
    """Discover EC2 Volumes."""
    try:
        account_id = request.args.get('resourceAccount')
        region = request.args.get('resourceRegion')
        argument_name = request.args.get('argument_name')
        argument_value = request.args.get('argument_value')

        aws_service = AWSService(region, account_id)
        repository = AWSResourceRepository(db)

        # Discover Volumes
        volume_data = aws_service.discover_volumes()

        # Save to database
        repository.clear_resources(account_id, region, argument_name, argument_value)
        repository.save_resource(
            account_id=account_id,
            region=region,
            json_data=volume_data,
            argument_name=argument_name,
            argument_value=argument_value,
            attributes='EC2_Volumes'
        )

        return jsonify({"message": "Volume discovery completed successfully"}), 200
    except Exception as e:
        logger.error(f"Error in Volume discovery: {e}")
        return jsonify({"error": str(e)}), 500

@ec2_discovery_bp.route('/api/discover_ec2', methods=['POST'])
@require_api_key
def discover_ec2():
    """Discover EC2 Instances."""
    try:
        account_id = request.args.get('resourceAccount')
        region = request.args.get('resourceRegion')
        argument_name = request.args.get('argument_name')
        argument_value = request.args.get('argument_value')

        aws_service = AWSService(region, account_id)
        repository = AWSResourceRepository(db)

        # Discover EC2 instances
        instances = aws_service.discover_instances()

        # Save to database
        repository.clear_resources(account_id, region, argument_name, argument_value)
        
        # Save each instance
        for reservation in instances:
            for instance in reservation['Instances']:
                repository.save_resource(
                    account_id=account_id,
                    region=region,
                    json_data=instance,
                    argument_name=argument_name,
                    argument_value=argument_value,
                    attributes='EC2',
                    res_id=instance['InstanceId']
                )

        return jsonify({"message": "EC2 instance discovery completed successfully"}), 200
    except Exception as e:
        logger.error(f"Error in EC2 instance discovery: {e}")
        return jsonify({"error": str(e)}), 500

@ec2_discovery_bp.route('/api/discover_ec2_type', methods=['POST'])
@require_api_key
def discover_ec2_type():
    """Discover EC2 Instance Types."""
    try:
        account_id = request.args.get('resourceAccount')
        region = request.args.get('resourceRegion')
        argument_name = request.args.get('argument_name')
        argument_value = request.args.get('argument_value')

        aws_service = AWSService(region, account_id)
        repository = AWSResourceRepository(db)

        # Discover instance types
        instance_types = aws_service.discover_instance_types()

        # Save to database
        repository.clear_resources(account_id, region, argument_name, argument_value)
        
        # Save instance types
        repository.save_resource(
            account_id=account_id,
            region=region,
            json_data=instance_types,
            argument_name=argument_name,
            argument_value=argument_value,
            attributes='EC2_type'
        )

        return jsonify({"message": "EC2 instance types discovery completed successfully"}), 200
    except Exception as e:
        logger.error(f"Error in EC2 instance types discovery: {e}")
        return jsonify({"error": str(e)}), 500 