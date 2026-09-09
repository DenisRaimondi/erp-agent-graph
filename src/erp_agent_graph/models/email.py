"""Email model.

The Mailpit search API returns Mailpit field names (``ID``, ``Subject``, ``From``,
``Created``). The aliases below map them onto domain-friendly Python names, so a
raw search payload can be validated directly with ``Email.model_validate(...)``.
"""

from datetime import datetime

from pydantic import AliasPath, BaseModel, ConfigDict, Field


class Email(BaseModel):
    """One message as returned by Mailpit's ``/api/v1/search`` endpoint.

    ``populate_by_name`` allows building an instance with the Python field names
    instead of the Mailpit aliases, which is what tests need in order to create
    fake emails without hand-writing Mailpit JSON.
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    # Mailpit IDs are alphanumeric strings, e.g. "6Ie89Hdz1R1WMrpkUS2hpJ".
    id: str = Field(alias="ID")
    subject: str = Field(alias="Subject")
    # "From" is an object {"Name": ..., "Address": ...}; AliasPath flattens it.
    sender: str = Field(validation_alias=AliasPath("From", "Address"))
    created_at: datetime = Field(alias="Created")
    attachments: int = Field(default=0, alias="Attachments")

    # Neither field is returned by the search endpoint: they are filled in from
    # GET /api/v1/message/{ID}, which returns "Text" and "HTML".
    body: str = ""
    html: str | None = None

    def to_prompt(self) -> str:
        return f"From: {self.sender}\nSubject: {self.subject}\nBody: {self.body}HTML: {self.html}"
