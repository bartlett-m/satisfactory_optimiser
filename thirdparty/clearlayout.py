# from https://stackoverflow.com/a/9383780
# [accessed 2025-01-06 at 13:32]

def clear_layout(layout):
    '''Removes and deletes every widget in a pyside6 layout'''
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clear_layout(item.layout())
