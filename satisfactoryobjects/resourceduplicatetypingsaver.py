from typing import Iterable


def resource_duplicate_typing_saver(
    unencapsulated_resources: Iterable[str]
) -> Iterable[str]:
    '''For each string in the iterable, prepend Desc_ and append _C'''
    return map(
        lambda centre_str: f'Desc_{centre_str}_C',
        unencapsulated_resources
    )
