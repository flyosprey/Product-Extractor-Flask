import re


class UserInputValidator:
    __slots__ = ("RESTRICTED_WORDS",)

    def __init__(self):
        self.RESTRICTED_WORDS = ("drop", "create", "role", "database", "insert", "alter", "select")

    @staticmethod
    def valid_extract_args(args):
        if "url" in args:
            if re.search(r"https?://zamorskiepodarki\.com/uk/.+?/.+?/", args["url"]):
                return True
        return False

    def valid_show_args(self, args):
        if "limit" in args:
            if args["limit"].isnumeric():
                if args.get("category_name"):
                    if self._check_restricted_words(args["category_name"]):
                        return False
                if args.get("title"):
                    if self._check_restricted_words(args["title"]):
                        return False
                return True
        return False

    def _check_restricted_words(self, text):
        for word in self.RESTRICTED_WORDS:
            if word in text.lower():
                return True
        return False