from flask import Flask, jsonify, request

vault = Flask(__name__)

# Имитация защищенного облачного сервиса метаданных и хранилища ключей (AWS IMDS / HashiCorp Vault)
INTERNAL_SECRETS = {
    "latest/meta-data/iam/security-credentials/admin-role": {
        "Code": "Success",
        "LastUpdated": "2026-09-03T16:00:00Z",
        "Type": "AWS-HMAC",
        "AccessKeyId": "ASIAQEXAMPLEACCESSKEY2026",
        "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "Token": "FQoGZXIvYXdzEExampleSecurityTokenValue=="
    },
    "v1/database/credentials": {
        "db_host": "db-production-cluster.internal",
        "db_user": "pg_admin",
        "db_password": "SuperSecretInternalMasterPassword!2026#"
    }
}

@vault.route('/', methods=['GET'])
def index():
    return jsonify({
        "service": "Internal Infrastructure Metadata & Key Management Service",
        "security_policy": "ISOLATED_SUBNET_ONLY",
        "endpoints": list(INTERNAL_SECRETS.keys())
    })

@vault.route('/<path:subpath>', methods=['GET'])
def get_secret(subpath):
    if subpath in INTERNAL_SECRETS:
        return jsonify(INTERNAL_SECRETS[subpath])
    return jsonify({"error": "Secret not found or access denied"}), 404

if __name__ == '__main__':
    vault.run(host='0.0.0.0', port=8080)
