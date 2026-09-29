"""Party: de opdrachtgever (customer) met contactpersonen."""

from pydantic import Field

from ._basis import SetuModel
from .basis import Identifier
from .codes import EmailUseCode, LegalSchemeAgencyId


class PersonName(SetuModel):
    formatted_name: str


class Phone(SetuModel):
    formatted_number: str  # E.164, bijv. "+31201234567"


class Email(SetuModel):
    address: str
    use_code: EmailUseCode | None = None


class Communication(SetuModel):
    phone: list[Phone] | None = None
    email: list[Email] | None = None


class ContactPerson(SetuModel):
    name: PersonName
    communication: Communication | None = None
    role_code: str | None = None  # in dit bericht meestal "Authorized by"
    position_title: str | None = None


class LegalId(SetuModel):
    value: str
    scheme_agency_id: LegalSchemeAgencyId


class Party(SetuModel):
    id: list[Identifier] | None = Field(default=None, max_length=2)
    name: str | None = None
    legal_id: list[LegalId] = Field(min_length=1)
    person_contacts: list[ContactPerson] = Field(min_length=1)
