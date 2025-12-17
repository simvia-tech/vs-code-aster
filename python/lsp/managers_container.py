from managers import StatusBarManager, HoverManager, UpdateManager, SignatureManager, CompletionManager

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