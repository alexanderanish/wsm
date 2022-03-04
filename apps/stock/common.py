
from fastapi import Body, Request
from .managers.post import PostManager
# from .managers. import PostManager
from .managers.comment import CommentManager
from .managers.stock_page import StockPageManager
from .managers.flair import FlairManager

class StockController:

    def __init__(self, request: Request):
        self.request = request

    def post(self):
        return PostManager(self.request.app.db["post"])

    def stock_page(self):
        return StockPageManager(self.request.app.db["stockPage"])

    def comment(self):
        return CommentManager(self.request.app.db["comment"])
    
    def flair(self):
        return FlairManager(self.request.app.db["flair"])
    