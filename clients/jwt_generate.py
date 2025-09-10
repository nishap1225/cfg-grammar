import jwt
import datetime


def generate_jwt(signing_secret: str):
    expiration_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=3)
    payload = {
        "workspace_id": "4a6300f4-8a88-44c0-929b-3ad92b103861",
        "name": "frontend_jwt",
        "exp": expiration_time,
        "scopes": [
            {
                "type": "DATASOURCES:READ",
                "resource": "baby_names",
            },
        ],
    }

    return jwt.encode(payload, signing_secret, algorithm="HS256")
