from datetime import datetime, timedelta,UTC
import jwt
from pydantic import BaseModel


class JWTUtil:
    def __init__(self, secret_key: str, algorithm: str = 'HS256', token_expire_minutes: int = 30):
        self.__secret_key = secret_key
        self.__algorithm = algorithm
        self.__token_expire_minutes = token_expire_minutes

    def create_token(self, data: dict | BaseModel) -> str:
        if isinstance(data, dict):
            # 浅拷贝
            payload = data.copy()
        else:
            payload = data.model_dump()
        # payload.update({'exp': datetime.now(timezone('UTC')) + timedelta(minutes=self.__token_expire_minutes)})
        payload['exp'] = datetime.now(UTC) + timedelta(minutes=self.__token_expire_minutes)
        token = jwt.encode(payload, self.__secret_key, self.__algorithm)
        return token

    def get_payload(self, token: str, Schema: type[BaseModel] | None = None) -> dict | BaseModel:
        """
        获取payload
        :param token:
        :return:
        :raise jwt.ExpiredSignatureError: jwt.InvalidTokenError的子类，token过期
        :raise jwt.InvalidTokenError: token无效
        """
        payload = jwt.decode(token, self.__secret_key, [self.__algorithm])
        if Schema:
            payload = Schema(**payload)
        return payload