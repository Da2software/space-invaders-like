import unittest
from pygame import Rect
from src.kinematics.kinematics import (
    Animation,
    AnimationCollection,
    Animator,
    AnimationTransform,
    Curve,
    KeyFrame,
)


class AnimationTest(unittest.TestCase):
    def test_animation_creation(self):
        animation = Animation("test_animation", duration=1000, frames=20)
        self.assertEqual(animation.id, "test_animation")
        self.assertEqual(animation.get_duration(), 1000)
        self.assertEqual(animation.get_frame_size(), 20)

    def test_animation_creation_zero(self):
        animation = Animation("test_animation", duration=0, frames=20)
        self.assertEqual(animation.id, "test_animation")
        self.assertEqual(animation.get_duration(), 0)
        self.assertEqual(animation.get_frame_size(), 0)

    def test_set_duration(self):
        animation = Animation("test_animation", duration=1000, frames=20)
        animation.set_duration(2000)
        self.assertEqual(animation.get_duration(), 2000)
        self.assertEqual(animation.get_frame_size(), 20)

    def test_set_frames_size(self):
        animation = Animation("test_animation", duration=1000, frames=20)
        animation.set_frames_size(30)
        self.assertEqual(animation.get_duration(), 1000)
        self.assertEqual(animation.get_frame_size(), 30)

    def test_get_key_frame(self):
        animation = Animation("test_animation", duration=1000, frames=20)
        key_frame = KeyFrame(Rect(2, 2, 10, 10), Curve.linear)
        animation.set_key_frame("1", key_frame)
        frame = animation.get_key_frame("1")
        self.assertEqual(frame.frame.y, key_frame.frame.y)
        self.assertEqual(frame.frame.x, key_frame.frame.x)

    def test_get_frame_by_time(self):
        animation = Animation("test_animation", duration=1000, frames=20)
        key_frame = KeyFrame(AnimationTransform(10, 10, 10, 10), Curve.linear)
        animation.set_key_frame("3", key_frame)
        # key frame 3 is placed between 150 and 200 ms
        frame, curve = animation.get_frame_by_time(175)
        self.assertEqual(frame.frame.y, key_frame.frame.y)
        self.assertEqual(frame.frame.x, key_frame.frame.x)


class AnimationCollectionTest(unittest.TestCase):

    def test_collection_create(self):
        animation_collection = AnimationCollection([
            Animation("test_animation", duration=100, frames=20)
        ])
        animation = animation_collection.get_animation("test_animation")
        self.assertEqual(animation.get_duration(), 100)
        self.assertEqual(animation.get_frame_size(), 20)

    def test_collection_append(self):
        animation_collection = AnimationCollection()
        self.assertEqual(len(animation_collection), 0)
        animation_collection.append(
            Animation("test_animation", duration=100, frames=20))
        self.assertEqual(len(animation_collection), 1)

    def test_collection_pop(self):
        animation_collection = AnimationCollection([
            Animation("test_animation", duration=100, frames=20)
        ])
        self.assertEqual(len(animation_collection), 1)
        animation_collection.pop("test_animation")
        self.assertEqual(len(animation_collection), 0)

    def test_interation(self):
        animation_collection = AnimationCollection([
            Animation("test_animation1", duration=100, frames=20),
            Animation("test_animation2", duration=200, frames=50),
            Animation("test_animation3", duration=300, frames=100)
        ])
        for [idx, anim] in enumerate(animation_collection):
            self.assertEqual(anim.id, f"test_animation{idx + 1}")
            if anim.id == "test_animation2":
                self.assertEqual(anim.get_duration(), 200)
                self.assertEqual(anim.get_frame_size(), 50)


if __name__ == "__main__":
    unittest.main()
