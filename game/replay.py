"""Record and replay a car's position independently of the physics simulation."""

import math
from bisect import bisect_right


MAX_FRAMES = 5000


def validate_frames(frames):
    """Return JSON-compatible frames, or None when a recording is invalid."""
    if not isinstance(frames, (list, tuple)) or len(frames) > MAX_FRAMES:
        return None

    validated = []
    previous_time = -1.0
    for frame in frames:
        if not isinstance(frame, (list, tuple)) or len(frame) != 5:
            return None
        # Bounds also exclude NaN, infinity, booleans and impractical values.
        if any(type(value) not in (int, float) or not -100_000_000 <= value <= 100_000_000
               for value in frame):
            return None
        elapsed = frame[0]
        if elapsed < 0 or elapsed <= previous_time:
            return None
        validated.append(list(frame))
        previous_time = elapsed
    return validated


class ReplayRecorder:
    def __init__(self, interval=0.05):
        if not math.isfinite(interval) or interval < 0.0001:
            raise ValueError("Opptaksintervallet må være minst 0,0001 sekund.")
        self.interval = interval
        self._frames = []
        self._next_sample = 0.0

    def _record(self, elapsed, pose):
        x, y, angle, wheel_angle = pose
        frame = [
            round(elapsed, 4), round(x, 2), round(y, 2),
            round(angle, 4), round(wheel_angle, 2),
        ]
        if self._frames:
            last_time = self._frames[-1][0]
            if frame[0] < last_time:
                return
            if frame[0] == last_time:
                self._frames[-1] = frame
                return
        if len(self._frames) >= MAX_FRAMES:
            # Halve sample density to retain the start and end of long runs.
            self._frames = self._frames[::2]
            self.interval *= 2
        self._frames.append(frame)

    def capture(self, elapsed, pose):
        if elapsed + 1e-9 < self._next_sample:
            return
        self._record(elapsed, pose)
        # Preserve the sample cadence even when a physics step crosses the deadline.
        self._next_sample = (math.floor((elapsed + 1e-9) / self.interval) + 1) * self.interval

    def finish(self, elapsed, pose):
        self._record(elapsed, pose)
        return [frame.copy() for frame in self._frames]


class GhostReplay:
    def __init__(self, frames):
        self.frames = validate_frames(frames) or []
        self._times = [frame[0] for frame in self.frames]

    @staticmethod
    def _angle_between(start, end, ratio, turn):
        difference = (end - start + turn / 2) % turn - turn / 2
        return start + difference * ratio

    def pose_at(self, elapsed):
        """Interpolate between recorded samples. Hide the ghost after its run."""
        if not self.frames or elapsed > self._times[-1] + 1e-9:
            return None
        if elapsed <= self._times[0]:
            return tuple(self.frames[0][1:])
        if elapsed >= self._times[-1]:
            return tuple(self.frames[-1][1:])

        index = bisect_right(self._times, elapsed)
        before = self.frames[index - 1]
        after = self.frames[index]
        ratio = (elapsed - before[0]) / (after[0] - before[0])
        return (
            before[1] + (after[1] - before[1]) * ratio,
            before[2] + (after[2] - before[2]) * ratio,
            self._angle_between(before[3], after[3], ratio, math.tau),
            self._angle_between(before[4], after[4], ratio, 360.0) % 360.0,
        )
