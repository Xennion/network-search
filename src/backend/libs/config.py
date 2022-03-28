import yaml
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

# check if secrets manager enabled and setup cache
if os.environ.get("SECRETSMANAGER") == "true":
    if not os.environ.get("SECRETSMANAGER_PATH"):
        raise SystemExit(
            "ERROR: AWS Secrets Manager enabled but env variable SECRETSMANAGER_PATH missing"
        )
    _profile = os.environ.get("SECRETSMANAGER_PROFILE")
    _client = boto3.Session(profile_name=_profile).client("secretsmanager")
    _secret = _client.get_secret_value(
        SecretId=os.environ.get("SECRETSMANAGER_PATH"),
    )
    config = yaml.safe_load(_secret["SecretString"])
else:
    with open("./config.yml", "r") as file:
        config = yaml.safe_load(file)
