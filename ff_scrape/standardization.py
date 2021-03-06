import re

rating_parentheses = re.compile("\\(.*\\)")
rating_hyphen = re.compile(" - .*")


def standardize_rating(rating):
    rating = rating_parentheses.sub('', rating)
    rating = rating_hyphen.sub('', rating)
    rating = rating.strip()
    if rating == 'Teens':
        return 'T'
    elif rating == 'Everyone':
        return 'E'
    elif rating == 'Mature':
        return 'M'

    return rating

def standardize_status(status):
    status = status.strip()
    if status == 'WIP (Work in progress)':
        return 'WIP'
    elif status == 'Complete':
        status = 'Completed'
    elif status == "Updated":
        status = "WIP"
    return status

def standardize_genre(genre):
    genre = genre.strip()
    return genre

def standardize_character(character):
    character = character.strip()
    if character == '':
        character = None
    # todo: enhance this
    return character

def standardize_warning(warning):
    warning = warning.strip()
    warning = warning.replace(' / ', '/')
    if warning == 'No Archive Warnings Apply':
        warning = None
    if warning == 'Creator Chose Not To Use Archive Warnings':
        warning = None
    return warning

def standardize_category(category):
    category = category.strip()
    if category == 'Hogwarts House':
        category = None
    return category

def standardize_universe(universe):
    universe = universe.strip()
    if universe == 'Harry Potter - J. K. Rowling':
        universe = 'Harry Potter'
    if universe == 'balto':
        universe = 'Balto'
    return universe

# todo: add standardize pairing
