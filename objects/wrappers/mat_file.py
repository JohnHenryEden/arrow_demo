
from pydantic import BaseModel


class MatFile(BaseModel):
    file_path: str
    upload_file: str | None = None
