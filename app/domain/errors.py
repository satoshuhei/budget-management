class DomainError(Exception):
    pass


class InvalidStatusTransition(DomainError):
    pass


class BudgetOverrun(DomainError):
    pass


class PermissionDenied(DomainError):
    pass
