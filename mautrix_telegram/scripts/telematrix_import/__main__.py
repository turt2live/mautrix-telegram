import argparse
import sqlalchemy as sql
from sqlalchemy import orm

from mautrix_telegram.base import Base
from mautrix_telegram.config import Config
from mautrix_telegram.db import Portal, Message, Puppet, BotChat
from .models import ChatLink, TgUser, MatrixUser, Message as TMMessage, Base as TelematrixBase

parser = argparse.ArgumentParser(
    description="mautrix-telegram telematrix import script",
    prog="python -m scripts/telematrix_import")
parser.add_argument("-c", "--config", type=str, default="config.yaml",
                    metavar="<path>", help="the path to your mautrix-telegram config file")
parser.add_argument("-b", "--bot-id", type=int, required=True,
                    metavar="<id>", help="the telegram user ID of your relay bot")
parser.add_argument("-t", "--telematrix-database", type=str, default="sqlite:///database.db",
                    metavar="<url>", help="your telematrix database URL")
args = parser.parse_args()

config = Config(args.config, None, None)
config.load()

mxtg_db_engine = sql.create_engine(config.get("appservice.database", "sqlite:///mautrix-telegram.db"))
mxtg = orm.sessionmaker(bind=mxtg_db_engine)()
Base.metadata.bind = mxtg_db_engine

telematrix_db_engine = sql.create_engine(args.telematrix_database)
telematrix = orm.sessionmaker(bind=telematrix_db_engine)()
TelematrixBase.metadata.bind = telematrix_db_engine

chat_links = telematrix.query(ChatLink).all()
tg_users = telematrix.query(TgUser).all()
mx_users = telematrix.query(MatrixUser).all()
messages = telematrix.query(TMMessage).all()

telematrix.close()
telematrix_db_engine.dispose()

portals = {}

for chat_link in chat_links:
    if type(chat_link.tg_room) is str:
        print("Expected tg_room to be a number, got a string. Ignoring %s" % chat_link.tg_room)
        continue
    if chat_link.tg_room >= 0:
        print("Unexpected unprefixed telegram chat ID: %s, ignoring..." % chat_link.tg_room)
        continue
    tgid = str(chat_link.tg_room)
    if tgid.startswith("-100"):
        tgid = int(tgid[4:])
        peer_type = "channel"
        megagroup = True
    else:
        tgid = -chat_link.tg_room
        peer_type = "chat"
        megagroup = False

    portal = Portal(tgid=tgid, tg_receiver=tgid, peer_type=peer_type, megagroup=megagroup,
                    mxid=chat_link.matrix_room)
    portals[chat_link.tg_room] = portal
    mxtg.add(portal)

    bot_chat = BotChat(id=tgid, type=peer_type)
    mxtg.add(bot_chat)

for tm_msg in messages:
    try:
        portal = portals[tm_msg.tg_group_id]
    except KeyError:
        print("Found message entry %d in unlinked chat %d, ignoring..." % (tm_msg.tg_message_id, tm_msg.tg_group_id))
        continue
    tg_space = portal.tgid if portal.peer_type == "channel" else args.bot_id
    message = Message(mxid=tm_msg.matrix_event_id, mx_room=tm_msg.matrix_room_id,
                      tgid=tm_msg.tg_message_id, tg_space=tg_space)
    mxtg.add(message)

mxtg.add_all(Puppet(id=user.tg_id, displayname=user.name, displayname_source=args.bot_id)
             for user in tg_users)
mxtg.commit()
