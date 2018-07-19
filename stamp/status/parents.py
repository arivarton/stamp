class StatusColumn(object):
    def __init__(self):
        self.headline = ''
        self.width = 5
        self.alignment = '<'
        self.value = None
        self.time_format = '%H:%M'
        self.left_margin = 0
        self.right_margin = 1
        self.selected_workday = 0

    def __str__(self):
        return '{0}{1:{alignment}{width}}{2}'.format(self.left_margin*' ',
                                                     str(self.values[self.selected_workday]),
                                                     self.right_margin*' ',
                                                     alignment=self.alignment,
                                                     width=self.width)

    def __iter__(self):
        self.selected_workday = 0
        return self

    def __next__(self):
        if self.selected_workday < len(self.values):
            return_value = self.__str__()
            self.selected_workday += 1
            return return_value
        else:
            raise StopIteration

    def get_max_width(self):

