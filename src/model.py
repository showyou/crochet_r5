#!/usr/bin/env python
# -*- coding: utf-8 -*-

# データベース定義
import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker, mapper, relation
from sqlalchemy import MetaData
from sqlalchemy import Column, MetaData, Table, types, ForeignKey
from datetime import datetime

class TwitData(object):
    pass



metadata = sqlalchemy.MetaData()
twitData = Table("twitData", metadata,
            Column('id',   types.Integer, primary_key=True),
            Column('user', types.String(32)),
            Column('twit', types.String(140)),
            Column('time', types.String(32))
            )

def startSession():
    """
        >>> a = startSession()
        --start DB Session--
    """
    config = {"sqlalchemy.url":
            "sqlite:///:memory:"}

    engine = sqlalchemy.engine_from_config(config)
    dbSession = scoped_session(
                    sessionmaker(
                        autoflush = True,
                        autocommit = True,
                        bind = engine
                    )
                )

    mapper(TwitData, twitData)
    metadata.create_all(bind=engine)
    print("--start DB Session--")
    return dbSession

if __name__ == "__main__":
    import doctest
    doctest.testmod()

