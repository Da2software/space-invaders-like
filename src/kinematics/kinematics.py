from abc import ABC
from pygame import Rect
from typing import List
from enum import Enum
import copy


class Curve(Enum):
    linear = 1
    smooth = 2


class KeyFrame:
    def __init__(self, frame: Rect, curve: Curve):
        self.frame = frame
        self.curve = curve


class FrameMap:
    def __init__(self, key: str, start: int, end: int):
        self.key = key
        self.start = start
        self.end = end


class Animation:
    def __init__(self, animation_id: str, duration=500, frames=10):
        """
        Class tha contains animation info
        :param name(required): of animation, should be unique in a
        AnimatorCollection, format with underscore('_') instead of space and
        lower case.
        :param duration: milliseconds
        :param frames: take the duration time and create key points places
        """
        self.id = animation_id.replace(" ", "_").lower()
        self.__duration = duration
        self.__frames = frames
        self.__key_frames = {}
        self.__frame_mapping: List[FrameMap] = []
        self.__map_frames()

    def __str__(self):
        return (f"(id: {self.id},\n duration: {self.__duration},\n "
                f"frames: {self.__frames}")

    def set_duration(self, duration: int):
        """
        Set a new animation duration time
        :param duration:
        :return: None
        """
        self.__duration = duration
        self.__map_frames()

    def get_duration(self) -> int:
        return self.__duration

    def set_frames_size(self, size: int):
        """
        Sets a new key point slices
        :param size: new key points number
        :return: None
        """
        self.__frames = size
        self.__map_frames()

    def __map_frames(self):
        segment = round(self.__duration / self.__frames)
        self.__frame_mapping = []
        for key_f in range(0, self.__frames):
            self.__frame_mapping.append(
                FrameMap(str(key_f),
                         start=segment * key_f,
                         end=segment * (key_f + 1))
            )

    def __build_key_frames(self):
        # NOTE: maybe we don't need this later
        for key_p in range(0, self.__frames + 1):
            self.__key_frames[str(key_p)] = KeyFrame(Rect(0, 0, 0, 0),
                                                     Curve.linear)

    def set_key_frames(self, key: str, key_frame: KeyFrame):
        self.__key_frames[key] = key_frame

    def get_key_frame(self, key):
        return self.__key_frames[key]

    def get_frame_by_time(self, timer: int):
        """
        Get the key based on the timer of the animation
        :param timer: current animation time between start to end duration
        :return: KeyFrame
        """
        for map_f in self.__frame_mapping:
            if map_f.start >= timer < map_f.end:
                return self.__key_frames[map_f.key]
        raise KeyError(f"Key Frame not found!")

    @staticmethod
    def clone_frame(frame: Rect, curve: Curve):
        return KeyFrame(copy.deepcopy(frame), curve)


class AnimationCollection:
    def __init__(self, animations: List[Animation] = []):
        self.__animations = animations
        self.validate()
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.__animations):
            current_item = self.__animations[self.index]
            self.index += 1
            return current_item
        else:
            return StopIteration

    def validate(self):
        """
        check if all animations are unique
        :return: None
        """
        keys = []
        for anim in self.__animations:
            if anim.id in keys:
                raise KeyError(
                    f"{anim.id} already exist, ID need to be unique")

    def get_animation(self, key):
        for anim in self.__animations:
            if anim.id == key:
                return anim
        return None

    def append(self, item):
        self.__animations.append(item)

    def pop(self, key):
        for i, item in enumerate(self.__animations):
            if item.id == key:
                return self.__animations.pop(i)
        raise KeyError(f"Key not found: {key}")


class Animator(ABC):
    """
    use to create animated moves for any python sprite
    """

    def __init__(self):
        self.animations = AnimationCollection()
        self.delta = 0
        self.timer = 0
        self.current_anim: Animation | None = None
        self.last_anim: str | None = None

    def run_animation(self, anim_id: str):
        self.current_anim = self.animations.get_animation(anim_id)
        self.timer = 0

    def render(self, animated_subject: Rect):
        # first detect if time is out of the duration
        if self.timer >= self.current_anim.get_duration():
            # then we stop the animation
            self.timer = 0
            self.last_anim = self.current_anim.id
            self.current_anim = None

        # in case we don't have an animation then we just avoid run something
        if not self.current_anim:
            return
        # set all properties to the original component
        animated_subject.size = self.current_anim.get_frame_by_time(self.timer)

        self.timer += self.delta  # update timer
