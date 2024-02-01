from abc import ABC, abstractmethod

import pygame.transform
from pygame import Rect, Surface
from typing import List
from enum import Enum
from src.globals import GameVariables


class Curve(Enum):
    linear = 1
    smooth = 2


class AnimationTransform:
    def __init__(self, x=0, y=0, width=10, height=10, angle=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle
        self.__pivot = (0, 0)

    def set_pivot(self, x, y):
        if x < 0 or x > self.width:
            raise ValueError(f"x axis ({x}) pivot can not be out of the "
                             f"width limit ({self.width}) or less"
                             f"than 0")
        if y < 0 or y > self.height:
            raise ValueError(f"x axis ({y}) pivot can not be out of the "
                             f"height limit ({self.height}) or less"
                             f"than 0")
        self.__pivot = (x, y)

    def get_pivot(self):
        return self.__pivot


class KeyFrame:
    def __init__(self, frame: AnimationTransform = AnimationTransform(),
                 curve: Curve = Curve.linear):
        self.frame = frame
        self.curve = curve


class FrameMap:
    def __init__(self, key: str, start: int, end: int):
        self.key = key
        self.start = start
        self.end = end

    def __str__(self):
        return f"({self.key}, {self.start}, {self.end})"


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
        self.__build_key_frames()

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

    def get_frame_size(self) -> int:
        return len(self.__frame_mapping)

    def __map_frames(self):
        if self.__duration <= 0:
            return
        segment = round(self.__duration / self.__frames)
        self.__frame_mapping = []
        for key_f in range(0, self.__frames):
            self.__frame_mapping.append(
                FrameMap(str(key_f),
                         start=segment * key_f,
                         end=segment * (key_f + 1))
            )

    def __build_key_frames(self):
        if self.__duration <= 0:
            return
        for key_p in range(0, self.__frames + 1):
            self.__key_frames[str(key_p)] = KeyFrame()

    def set_key_frame(self, key: str, key_frame: KeyFrame):
        """
        key is basically a frame position from 0 to any number but
        in string format, because keyframes are saved in an object
        """
        self.__key_frames[key] = key_frame

    def get_key_frame(self, key) -> KeyFrame:
        return self.__key_frames[key]

    def get_frame_by_time(self, timer: int) -> (KeyFrame, str):
        """
        Get the key based on the timer of the animation
        :param timer: current animation time between start to end duration
        :return: KeyFrame
        """
        for map_f in self.__frame_mapping:
            if map_f.start <= timer < map_f.end:
                return self.__key_frames[map_f.key], map_f.key
        raise KeyError(f"Key Frame not found!")


class AnimationCollection:
    def __init__(self, animations: List[Animation] = None):
        if not animations:
            animations = []
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
            raise StopIteration

    def __len__(self):
        return len(self.__animations)

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
        self.timer = 0
        self.current_anim: Animation | None = None
        self.last_key_frame: str | None = None
        self.last_anim: str | None = None
        self.define_animations()

    @abstractmethod
    def define_animations(self):
        """
        Define all animations you object will use, and in order to create that
        use the {self.animations} value
        :return: None
        """
        pass

    def __do_transform(self, target: Rect, key_frame: KeyFrame):
        """
        Change/move rect properties to the expected position
        just adding or subtracting the values from the transform object.
        :param target: object to apply changes/moves
        :param transform: objects to pass the properties
        :return: None
        """
        if key_frame.curve == Curve.linear:
            target.y += key_frame.frame.y
            target.x += key_frame.frame.x
            target.width += key_frame.frame.width
            target.height += key_frame.frame.height
        elif key_frame.curve == Curve.smooth:
            target.move_ip(key_frame.frame.x, key_frame.frame.y)

        # rotation is complicated with just rects, we need to change tha

    def run_animation(self, anim_id: str):
        """
        Run a specific animation
        :param anim_id: animation ID
        :return: None
        """
        self.current_anim = self.animations.get_animation(anim_id)
        self.timer = 0

    def render_animation(self, animated_subject: Rect):
        """
        used to execute the animation and change frames according to the
        timer
        :param animated_subject: original {Rect} object to apply the animations
        :return: None
        """
        # first detect if time is out of the duration
        if self.current_anim and self.timer >= self.current_anim.get_duration():
            # then we stop the animation
            self.timer = 0
            self.last_anim = self.current_anim.id
            self.current_anim = None

        # in case we don't have an animation then we just avoid run something
        if not self.current_anim:
            return
        # set all properties to the original component
        frame, new_key = self.current_anim.get_frame_by_time(
            self.timer)
        if self.last_key_frame != new_key:
            self.__do_transform(target=animated_subject, key_frame=frame)
        self.last_key_frame = new_key
        self.timer += GameVariables().delta_time * 1000  # update timer on milliseconds
        print(self.timer)
