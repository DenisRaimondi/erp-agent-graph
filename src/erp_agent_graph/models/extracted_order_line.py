from datetime import date

from pydantic import BaseModel, Field


class ExtractedOrderLine(BaseModel):
    article_code: str | None = Field(
        description="The article code mentioned in the email. Leave it blank if it does "
        "not exist, or if you cannot tell which one it is: no code is better than a "
        "wrong one, a person will resolve it during the review."
    )
    description: str = Field(
        description="The description of the requested article as mentioned in the email"
    )
    quantity: int = Field(description="The quantity of the article requested in the mail", gt=0)
    requested_date: date | None = Field(description="The date the article needs to be shipped")
