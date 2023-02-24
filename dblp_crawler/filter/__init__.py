from .utils import map_person_publications


def drop_old_publications(summary, year):
    def callback(_, publication):
        if publication["year"] >= year:
            return publication

    return map_person_publications(summary, callback)
