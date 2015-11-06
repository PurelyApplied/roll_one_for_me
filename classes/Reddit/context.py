

class MentionContext:
    def __init__(self, tables, commands: list):
        self.tables = tables
        self.commands = commands
        self.stack = commands.copy()

    def unresolved(self) -> bool:
        """Is there still work to be done?"""
        return bool(self.stack)

