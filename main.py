import functools
from typing import List


class Photo:
    def __init__(self, index, orientation, tags):
        self.index = index
        self.orientation = orientation
        self.tags = tags
        self.common_tag_with = set()

    def __repr__(self):
        return "slide: " + str(self.index) + " -  has common tags with: [" + ", ".join(map(lambda c: str(c.index), self.common_tag_with)) + "]"

class Slide:
    def __init__(self, photos: List[Photo]):
        self.photos = photos

    @property
    def tags(self):
        result = set()
        for p in self.photos:
            result.update(set(p.tags))
        return result


class Solution:
    def __init__(self, slides: List[Slide]):
        self.slides = slides

    def calc_score(self) -> int:
        return sum(calc_interest(self.slides[i], self.slides[i+1]) for i in range(
            len(self.slides) - 1))


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
            orientation, num_of_tags, *tags = line.strip().split(" ")
            photo = Photo(index, orientation, tags)
            photos.append(photo)
        link_photos(photos)
        #print("done")
        #print(photos)
    return photos


def link_photos(photos):
    tag_dict = {}
    for p in photos:
        for t in p.tags:
            if t not in tag_dict:
                tag_dict.update({t: [p]})
            else:
                tag_dict[t].append(p)
    for p in photos:
        for t in p.tags:
            p.common_tag_with.update(tag_dict[t])
        p.common_tag_with.remove(p)
    return tag_dict


def write_solution(solution: Solution, filename: str):
    with open(filename, "w") as file:
        file.write(str(len(solution.slides)) + "\n")
        for slide in solution.slides:
            file.write(", ".join(str(s.index) for s in slide.photos) + "\n")


def solve(photos: List[Photo]) -> Solution:
    # temp test
    slides = []
    for photo in photos:
        slides.append(Slide([photo]))
    return Solution(slides)


def main():
    filename = "a_example.txt"
    photos = read_file(filename)
    print(f"Calculating for {filename}…")
    solution = solve(photos)
    print(f"Score of solution: {solution.calc_score()}")
    write_solution(solution, filename.replace(".txt", "_out.txt"))


if __name__ == '__main__':
    main()
