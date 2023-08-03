from passlib.context import CryptContext

pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

hash_object = CryptContext(schemes=["bcrypt"], deprecated="auto")
