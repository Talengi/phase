# -*- coding: utf-8 -*-



class TransmittalError(Exception):
    pass


class MissingRevisionsError(TransmittalError):
    pass


class InvalidRevisionsError(TransmittalError):
    pass


class InvalidCategoryError(TransmittalError):
    pass


class InvalidRecipientError(TransmittalError):
    pass


class InvalidContractNumberError(TransmittalError):
    pass
