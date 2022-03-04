import asyncio
import requests
import os
from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Callable, Optional, Type

from dotenv import load_dotenv
load_dotenv('.env')

router = APIRouter()

DOMAIN = 'https://www.alphavantage.co/'
APIKEY = os.getenv('ALPHA_API_KEY')

@router.get("/stock-search", response_description="Search all the Stocks from external APIs")
async def search(request: Request, keyword: str = None):
    # url = 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=tesco&apikey=demo'
    url = DOMAIN + 'query?function=SYMBOL_SEARCH&keywords=' + keyword + '&apikey=' + APIKEY
    r = requests.get(url)
    data = r.json()
    return data


@router.get("/stock-details", response_description="Get the Stock Details from external APIs")
async def search(request: Request, stock: str):
     # url = 'https://www.alphavantage.co/query?function=OVERVIEW&symbol=IBM&apikey=demo'
    url = DOMAIN + 'query?function=OVERVIEW&symbol=' + stock + '&apikey=' + APIKEY
    r = requests.get(url)
    data = r.json()
    return data


@router.get("/stock-price", response_description="Get the Stock Price from external APIs")
async def search(request: Request, stock: str, interval: Optional[str] = None):
    # url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=demo'
    if not interval:
        interval = '5min'
    url = DOMAIN + 'query?function=TIME_SERIES_INTRADAY&symbol=' + stock + '&interval='+ interval +'&apikey=' + APIKEY
    r = requests.get(url)
    data = r.json()
    return data