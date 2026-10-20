from fastapi import FastAPI, HTTPException
from supadata import Supadata
from dotenv import load_dotenv
import os 
import re
from pydantic import BaseModel, AnyHttpUrl, Field, field_validator
from typing import Annotated, Any
from urllib.parse import parse_qs


load_dotenv()
app = FastAPI()

class Data(BaseModel):
    URL: Annotated[AnyHttpUrl, Field(description="Requires a valid youtube video URL", examples=["https://www.youtube.com/watch?v=U-XqKFPv2KM","https://www.youtube.com/watch?v=kpIy4pmP62Y" ])]

    @field_validator("URL", mode="before")
    @classmethod
    def add_url_scheme(cls, value: Any) -> Any:
        if isinstance(value, str):
            value = value.strip()
            if not value.lower().startswith(("http://", "https://")):
                value = f"https://{value}"
        return value

    @field_validator("URL")
    @classmethod
    def validate_youtube_url(cls, value: AnyHttpUrl) -> AnyHttpUrl:
        host = value.host.lower().removeprefix("www.")
        if host not in {"youtube.com", "youtu.be"}:
            raise ValueError("URL must be a YouTube video URL")

        video_id = ""
        if host == "youtu.be":
            video_id = value.path.strip("/")
        elif value.path == "/watch":
            video_id = parse_qs(value.query).get("v", [""])[0]
        else:
            match = re.fullmatch(r"/(?:embed|v|shorts)/([\w-]{11})", value.path)
            if match:
                video_id = match.group(1)

        if not re.fullmatch(r"[\w-]{11}", video_id):
            raise ValueError("URL must contain a valid YouTube video ID")
        return value

SUPADATA_API_KEY = os.getenv("SUPADATA_API_KEY")


@app.get("/")
def home():
    return {"msg":"GeoidX API is working "}


@app.post("/gettranscript")
def get_transcript(data: Data):
    if not SUPADATA_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Transcript service is not configured.",
        )

    supadata = Supadata(api_key=SUPADATA_API_KEY)

    result = supadata.transcript(
        url=str(data.URL),
        text=True
    )
    return result
