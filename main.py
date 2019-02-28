import functools
from typing import List


class Photo:
    def __init__(self, index, orientation, tags):
        self.index = index
        self.orientation = orientation
        self.tags = tags


class Slide:
    def __init__(self, photos: List[Photo]):
        self.photos = photos

    @functools.lru_cache
    @property
    def tags(self):
        return {p.tags for p in self.photos}


class Solution:
    def __init__(self, slides: List[Slide]):
        self.slides = slides


def calc_interest(slide1: Slide, slide2: Slide) -> int:
    tags1 = slide1.tags
    tags2 = slide2.tags
    intersection = tags1.intersection(tags2)
    interest_1 = tags1.difference(intersection)
    interest_3 = tags2.intersection(intersection)
    interest_2 = intersection
    return min(len(interest_1), len(interest_2), len(interest_3))


def read_file(filename: str) -> List[Photo]:
    with open(filename, "r") as file:
        lines = file.readlines()
        # num_of_photos = int(lines[0])
        photos = []
        for index, line in enumerate(lines[1:]):
            orientation, num_of_tags, *tags = line.split(" ")
            photo = Photo(index, orientation, tags)
            photos.append(photo)
    return photos


def write_solution(solution: Solution, filename: str):
    with open(filename, "w") as file:
        file.write(str(len(solution.slides)))
        for slide in solution.slides:
            file.write(", ".join(s.index for s in slide.photos))


def main():
    print("This code does nothing right now!")


if __name__ == '__main__':
    main()
