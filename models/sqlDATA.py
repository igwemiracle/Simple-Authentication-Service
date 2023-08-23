from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
Base = declarative_base()


class User(Base):
    __tablename__ = "signin"
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String)
    email = sa.Column(sa.String, unique=True, index=True)
    hash_password = sa.Column(sa.String)
    confirm_password = sa.Column(sa.String)
    is_logged_in = sa.Column(sa.Boolean, default=False)
