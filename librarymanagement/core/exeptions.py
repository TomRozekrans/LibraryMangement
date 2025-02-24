class InvalidBookIdException(Exception):
    def __init__(self, id):
        self.id = id
        super().__init__(f"Invalid book id: {id}")


class LastBookGenreDeleteException(Exception):
    def __init__(self, id):
        self.id = id
        super().__init__(f"Last book in genre cannot be deleted: {id}")
