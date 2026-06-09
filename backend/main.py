from fastapi import FastAPI
from supadata import Supadata
from dotenv import load_dotenv
import os 
from pydantic import BaseModel, AnyHttpUrl, Field
from typing import Annotated


load_dotenv()
app = FastAPI()

class Data(BaseModel):
    URL: Annotated[AnyHttpUrl, Field(description="Requires a valid youtube video URL", examples=["https://www.youtube.com/watch?v=U-XqKFPv2KM","https://www.youtube.com/watch?v=kpIy4pmP62Y" ])]

SUPADATA_API_KEY = os.getenv("SUPADATA_API_KEY")


@app.get("/")
def home():
    return {"msg":"GeoidX API is working "}


@app.post("/gettranscript")
def get_transcript(Data):
    print(Data)
    supadata = Supadata(api_key=SUPADATA_API_KEY)

    result = supadata.transcript(
        url=Data,
        text=True
    )
    return result
