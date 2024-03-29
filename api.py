import os.path
from typing import Annotated

from fastapi import FastAPI, File
from paddleocr import PaddleOCR
from pydantic import BaseModel

DIRECTORY = os.path.dirname(__file__)
MODEL_DIRECTORY = os.getenv("OCRRA_MODEL_DIR", os.path.join(DIRECTORY, "model"))

app = FastAPI()
ocr = PaddleOCR(
    use_angle_cls=True,
    lang="latin",
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
async def recognize(image: Annotated[bytes, File()]):
    return [
        RecognitionResult(
            text=text,
            score=score,
            contour=[Point(x=x, y=y) for x, y in points]
        )
        for result in ocr.ocr(image, cls=True)
        for points, (text, score) in result
    ]
