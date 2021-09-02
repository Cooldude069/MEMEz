from settings.defaultSettings import *
import pymongo
from pymongo import MongoClient
import os


class settingsManager:
    def __init__(self, server_id: int) -> None:
        self.cluster = MongoClient(os.environ.get("mongo_url"))
        self.serverID = server_id

    def getAllSettings(self) -> dict:
        db = self.cluster["main"]
        collection = db["settings"]
        settings = collection.find_one({"_id": 0})
        settings = settings["settings"]
        if str(self.serverID) in settings:
            return settings[str(self.serverID)]
        else:
            return defaultSettings

    def updateSetting(self, category: str, key: str, value) -> None:
        settings = self.getAllSettings()
        if category in settings:
            if key in settings[category]:
                settings[category][key] = value

        collection = self.cluster["main"]["settings"]
        allSettings = collection.find_one({"_id": 0})
        allSettings["settings"][str(self.serverID)] = settings
        collection.update_one({"_id": 0}, {"$set": {"settings": allSettings}})
