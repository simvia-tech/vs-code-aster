from managers import (
    CompletionManager,
    HoverManager,
    SignatureManager,
    StatusBarManager,
    UpdateManager,
)


class ManagerContainer:
    """
    Central container for all feature classes.
    Initialize all managers
    """

    def __init__(self):
        self.status_bar = StatusBarManager()
        self.hover = HoverManager()
        self.update = UpdateManager()
        self.signature = SignatureManager()
        self.completion = CompletionManager()
