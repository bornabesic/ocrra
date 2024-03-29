import os.path
from typing import Annotated

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from paddleocr import PaddleOCR
from pydantic import BaseModel

DIRECTORY = os.path.dirname(__file__)
MODEL_DIRECTORY = os.getenv("OCRRA_MODEL_DIR", os.path.join(DIRECTORY, "model"))

app = FastAPI()
ocr = PaddleOCR(
    use_angle_cls=True,
    lang="latin",
    show_log=False,
    det_model_dir=os.path.join(MODEL_DIRECTORY, "det"),
    rec_model_dir=os.path.join(MODEL_DIRECTORY, "rec"),
    cls_model_dir=os.path.join(MODEL_DIRECTORY, "cls")
)


class Point(BaseModel):
    x: float
    y: float


class RecognitionResult(BaseModel):
    text: str
    score: float
    contour: list[Point]


@app.post("/recognize")
async def recognize(image: Annotated[UploadFile, File()]):
    try:
        results = ocr.ocr(image.file.read(), cls=True)
    except Exception:
        raise HTTPException(status_code=400, detail="Unable to apply OCR on the uploaded file.")

    return [
        RecognitionResult(
            text=text,
            score=score,
            contour=[Point(x=x, y=y) for x, y in points]
        )
        for result in results
        for points, (text, score) in result
    ]
