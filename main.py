import logging
import os

import hikari
import lightbulb
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = hikari.Intents.ALL

client = lightbulb.BotApp(prefix="h.", intents=intents, token=TOKEN, help_class=None,
                          owner_ids=[444550944110149633, 429935667737264139, 603635602809946113])
logging.getLogger("hikari").setLevel("ERROR")
logging.getLogger("lightbulb").setLevel("ERROR")

client.load_extensions_from("cogs")

client.run()
