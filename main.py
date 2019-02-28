import functools
import sys
import random
from typing import List, Set


tag_freq = {}
avg_tag_freq = 1
tag_dict = {}


class Photo:
    def __init__(self, index, is_vert: bool, tags):
        self.index = index
        self.is_vert = is_vert
        self.tags = tags

    @property  # it's actually not a fast property
    def common_tag_with(self):
        returned = set()
        for t in self.tags:
            returned.update(tag_dict[t])
        returned.remove(self)
        return returned

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

    @property
    def is_pair(self) -> bool:
        return len(self.photos) == 2  # can only be 1 or 2


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


def calc_interest2(photo1: Photo, photo2: Photo) -> int:
    tags1 = set(photo1.tags)
    tags2 = set(photo2.tags)
    intersection = tags1.intersection(tags2)
    interest_1 = tags1.difference(intersection)
    interest_3 = tags2.intersection(intersection)
    interest_2 = intersection
    return min(len(interest_1), len(interest_2), len(interest_3))


def calc_tag_worth(tags):
    return sum(tag_freq[t] for t in tags)


def calc_interest_smart(slide1: Slide, slide2: Slide) -> int:
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
        photos = []
        for index, line in enumerate(lines[1:]):
            orientation, num_of_tags, *tags = line.strip().split(" ")
            photo = Photo(index, orientation == "V", tags)
            photos.append(photo)
            update_tag_freq(tags)
        link_photos(photos)
        calc_avg_freq()
    return photos


def update_tag_freq(tags):
    global tag_freq
    for t in tags:
        if t not in tag_freq:
            tag_freq[t] = 0
        else:
            tag_freq[t] += 1


def calc_avg_freq():
    global tag_freq
    global avg_tag_freq
    frequencies = list(tag_freq.values())
    avg_tag_freq = sum(frequencies)/len(frequencies)


def link_photos(photos):
    for p in photos:
        for t in p.tags:
            if t not in tag_dict:
                tag_dict[t] = [p]
            else:
                tag_dict[t].append(p)


def write_solution(solution: Solution, filename: str):
    with open(filename, "w") as file:
        file.write(str(len(solution.slides)) + "\n")
        for slide in solution.slides:
            file.write(" ".join(str(s.index) for s in slide.photos) + "\n")


def solve_greedy_grouping(photos: List[Photo], grouping_threshold: int, max_group: int) -> Solution:
    # temp test
    slides_groups = []
    slides=[]
    group = [photos.pop()]
    while len(photos) > 0:
        group_photos = set()
        for photo in group:
            group_photos = group_photos.union(photo.common_tag_with)
        group_photos = group_photos.intersection(photos)
        best_score = 0
        best_photo = None
        best_position = 0
        for photo in group_photos:
            for position in range(len(group)-1):
                new_interest = calc_interest2(photo, group[position]) + calc_interest2(photo, group[position+1]) \
                               - calc_interest2(group[position], group[position+1])
                if new_interest>best_score:
                    best_score = new_interest
                    best_photo = photo
                    best_position = position+1
            start_interest = calc_interest2(photo, group[0])
            end_interest = calc_interest2(photo, group[-1])
            if start_interest > best_score:
                best_score = start_interest
                best_photo = photo
                best_position = 0
            if end_interest > best_score:
                best_score = end_interest
                best_photo = photo
                best_position = len(group)+1
        if best_score>grouping_threshold:
            photos.remove(best_photo)
            group.insert(best_position, best_photo)
            if len(group)>max_group:
                slides_groups.append(group)
                print(len(photos))
                group = [photos.pop()]
        else:
            slides_groups.append(group)
            print(len(photos))
            group = [photos.pop()]


    for group in slides_groups:
        for photo in group:
            slides.append(Slide([photo]))
    return Solution(slides)


def solve_greedy_picks(photos: List[Photo]) -> Solution:
    remaining_photos = photos[:]  # clone
    remaining_vertical_photos = [p for p in photos if p.is_vert]

    def pick_random_slide() -> Slide:
        random_photo: Photo = random.choice(remaining_photos)
        remaining_photos.remove(random_photo)  # I hope this works
        if random_photo.is_vert:
            remaining_vertical_photos.remove(random_photo)  # I hope this works
            another_random_vertical_photo = random.choice(remaining_vertical_photos)
            remaining_vertical_photos.remove(another_random_vertical_photo)  # I hope this works
            remaining_photos.remove(another_random_vertical_photo)  # I hope this works
            return Slide([random_photo, another_random_vertical_photo])
        else:
            return Slide([random_photo])

    last_slide = pick_random_slide()
    slides = [last_slide]
    while remaining_photos:
        # find other photo to get best transition interest score
        best_possible_transition_score = -1
        best_possible_slide = None
        nominees = last_slide.photos[0].common_tag_with
        if last_slide.is_pair:
            nominees.update(last_slide.photos[1].common_tag_with)
        nominees = nominees.intersection(remaining_photos)
        if not nominees:  # "dead end"
            nominees = [random.choice(remaining_photos)]  # to just take another photo
        for photo in nominees:
            if photo.is_vert:
                # choose another random vertical photo
                remaining_vertical_photos.remove(photo)  # temporarily
                another_random_vertical_photo = random.choice(remaining_vertical_photos)
                remaining_vertical_photos.append(photo)
                possible_slide = Slide([photo, another_random_vertical_photo])
            else:
                possible_slide = Slide([photo])
            possible_score = calc_interest(last_slide, possible_slide)
            if possible_score > best_possible_transition_score:
                best_possible_transition_score = possible_score
                best_possible_slide = possible_slide
        for photo in best_possible_slide.photos:
            remaining_photos.remove(photo)
            if photo.is_vert:
                remaining_vertical_photos.remove(photo)
        last_slide = best_possible_slide
        slides.append(last_slide)
    return Solution(slides)


def main():
    # filename = "b_lovely_landscapes.txt"
    filename = "c_memorable_moments.txt"
    # filename = "d_pet_pictures.txt"
    # filename = "e_shiny_selfies.txt"
    photos = read_file(filename)
    print(f"Calculating for {filename}…")
    solution = solve_greedy_picks(photos)
    print(f"Score of solution: {solution.calc_score()}")
    write_solution(solution, filename.replace(".txt", "_out.txt"))


if __name__ == '__main__':
    main()
