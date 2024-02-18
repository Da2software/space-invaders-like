from abc import ABC, abstractmethod

import pygame.transform
import json
from pygame import Rect, Surface
from typing import List
from enum import Enum
from src.globals import GameVariables

GLOBALS = GameVariables()


class Curve(Enum):
    linear = 1
    smooth = 2


class AnimationTransform:
    def __init__(self, x=0, y=0, width=0, height=0, angle=0):
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
                 curve: Curve = Curve.linear, key_point=False):
        self.frame = frame
        self.curve = curve
        self.key_point = key_point


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

    def get_key_frame_list(self):
        return self.__key_frames

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

    def set_key_frame(self, key: str, key_frame: KeyFrame,
                      key_point: bool = False):
        """
        key is basically a frame position from 0 to any number but
        in string format, because keyframes are saved in an object
        """
        key_frame.key_point = key_point
        self.__key_frames[key] = key_frame

    def get_key_frame(self, key) -> KeyFrame:
        return self.__key_frames[key]

    def get_frame_by_time(self, timer: int) -> (KeyFrame, str):
        """
        Get the key based on the timer of the animation
        :param timer: current animation time between start to end duration
        :return: KeyFrame
        """
        last_key = '0'
        for map_f in self.__frame_mapping:
            if map_f.start <= timer < map_f.end:
                last_key = map_f.key
                return self.__key_frames[map_f.key], map_f.key
        # return empty/default frame
        return KeyFrame(), last_key


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
        # last time frame helps to match the timer with the frame to run
        self.last_time_frame: str | None = None
        # this takes the last animation name/id
        self.last_anim: str | None = None
        # last key frame takes the last frame with key point property to be
        # able to create a smooth move animation
        self.last_key_frame: None | KeyFrame = None
        self.set_name = "basic"
        self.define_animations()
        self.__on_pause = False
        self.loop = False

    @staticmethod
    def get_animation_set(set_name):
        animation_set = {}
        with open(f'src/assets/animations/{set_name}.json') as f:
            animation_set = json.load(f)
        return animation_set

    def define_animations(self):
        """
        This creates all the animations based on the json files
        :return: None
        """
        animation_sets = self.get_animation_set(self.set_name)
        common_sets = self.get_animation_set("common")
        """
        animation_set = [
            {
                "name": str,
                "duration": int,
                "frames": int,
                "key_frames": [
                    { 
                        "frame": int, 
                        "x": int, 
                        "y": int, 
                        "rotate": int, 
                        "w": int, 
                        "h": int,
                        "curve": "smooth" | "linear"
                    }
                ]
            }
        ]
        """
        # loop the animation set to create the animations
        for anim_set in animation_sets:
            # there is some animation that can be reusable
            if "common" in anim_set:
                # that's why we have a common set
                anim_set = common_sets[anim_set["common"]]
            new_animation = Animation(
                animation_id=anim_set["name"],
                duration=anim_set["duration"],
                frames=anim_set["frames"])
            # each animation set has key frames
            for key_frame in anim_set["key_frames"]:
                # each frame has a transform parameters
                transform = AnimationTransform(key_frame["x"], key_frame["y"])
                # width and height are optional
                if "w" in key_frame:
                    transform.width = key_frame["w"]
                if "h" in key_frame:
                    transform.height = key_frame["h"]
                if "rotate" in key_frame:
                    transform.angle = key_frame["rotate"]
                # in case we set a curve time
                curve = Curve.smooth
                if "curve" in key_frame and key_frame["curve"] == "linear":
                    curve = Curve.linear
                # then we set the frame, also set as key point
                new_animation.set_key_frame(
                    key_frame["frame"],
                    KeyFrame(transform, curve),
                    True
                )
            # here we add the animation to the collection
            self.make_smooth(new_animation)  # smooth process
            self.animations.append(new_animation)

    @staticmethod
    def make_smooth(animation: Animation):
        """
        Triggered after define an animation, this takes each smoth key point and
        preprocess the middle frames to generate the smooth effect.
        :return:
        """
        anim_frames = animation.get_key_frame_list()
        # in order to do the smooth animation the middle frames should from
        # the smooth frame [2,-,-,-,5,-,-,5] => [2,1.66,1.66,1.66,0,2.,2.5,0]
        # always start with 0 and go to the positive or negative value
        smooth_point_key: str | None = None
        middle_frames: List[str] = []  # just save indexes

        for key in list(animation.get_key_frame_list().keys())[::-1]:
            if anim_frames[key].key_point:
                # take current key point that is smooth
                smooth_point_key = key if (
                        anim_frames[key].curve == Curve.smooth) else None
                # each time we reach a key point we need override middle frames
                middle_frames_size = len(middle_frames)
                # just in case we have middle frames
                if middle_frames_size > 0:
                    smooth_point = anim_frames[smooth_point_key]
                    # formula: middle_frame = smooth_key / middle_frames_count
                    new_transform = AnimationTransform()
                    for obj_key in smooth_point.frame.__dict__.keys():
                        point_val = smooth_point.frame.__dict__[obj_key]
                        if obj_key == '_AnimationTransform__pivot':
                            continue
                        # avoid dive by zero error
                        new_transform.__dict__[obj_key] = (
                                point_val / middle_frames_size) if (
                                point_val != 0) else 0
                    # set the mew value over all middle frames
                    for frame_key in middle_frames:
                        # update middle frame
                        curr_frame = animation.get_key_frame(frame_key)
                        curr_frame.frame = new_transform
                        animation.set_key_frame(frame_key, curr_frame)
                    # reset middle points to work with the new key point
                    middle_frames = []
                    # set smooth frame to zero, because middle frames has
                    # the new movement
                    anim_frames[
                        smooth_point_key].frame = AnimationTransform()
            # in case we found a smooth point we can now map the middle frames
            elif smooth_point_key and not anim_frames[key].key_point:
                middle_frames.append(key)

    @staticmethod
    def __do_transform(target: Rect, key_frame: KeyFrame):
        """
        Change/move rect properties to the expected position
        just adding or subtracting the values from the transform object.
        :param target: object to apply changes/moves
        :param transform: objects to pass the properties
        :return: None
        """
        target.move_ip(key_frame.frame.x, key_frame.frame.y)
        # TODO: rotation is complicated with just rects, we need to change
        #  that and also add the width and height transform

    def run_animation(self, anim_id: str, loop: bool = False):
        """
        Run a specific animation
        :param anim_id: animation ID
        :param loop: set the animation as a loop
        :return: None
        """
        self.current_anim = self.animations.get_animation(anim_id)
        self.timer = 0
        self.loop = loop

    def stop_animation(self):
        # then we stop the animation
        self.timer = 0
        self.last_anim = self.current_anim.id
        self.current_anim = None

    def pause_animation(self):
        self.__on_pause = True

    def continue_animation(self):
        self.__on_pause = False

    def render_animation(self, animated_subject: Rect):
        """
        used to execute the animation and change frames according to the
        timer
        :param animated_subject: original {Rect} object to apply the animations
        :return: None
        """
        if self.__on_pause:
            return
        # first detect if time is out of the duration
        if self.current_anim and self.timer >= self.current_anim.get_duration():
            if self.loop:
                self.run_animation(self.current_anim.id, True)
            else:
                self.stop_animation()

        # in case we don't have an animation then we just avoid run something
        if not self.current_anim:
            return
        # set all properties to the original component
        frame, time_key = self.current_anim.get_frame_by_time(
            self.timer)

        # to create a smooth animation version we need to take the last key
        # transform and apply it during the next key point appears
        # in case we are in different time key then we need to render
        # the new key, but
        if frame.key_point and self.last_time_frame != time_key:
            self.last_key_frame = frame
        if self.last_time_frame != time_key and frame.curve == Curve.linear:
            self.__do_transform(target=animated_subject, key_frame=frame)
        self.last_time_frame = time_key
        # frame rate is 60, then 60 frames = 1000 ms(1s),
        # result 1 frame = 16.666666667
        self.timer += 16.666666667  # update timer
        print(self.timer, end="\r")
