from typing import Any
from dxfwrite import DXFEngine as dxf
from utils import end_point_of_line, normalize_vector, vector_difference, vector_sum
import math


class Branch:
    def __init__(
        self,
        start_point: tuple[float],
        length: float,
        angle: float,
        count_beam: int,
        pannel_gap=1.2,
        beam_gap=2.33,
        beam_length=6.33,
        beam_width=4.83,
        drawing=dxf.drawing("yoshimura_pattern.dxf"),
    ) -> None:
        self.start_point = start_point
        self.end_point = end_point_of_line(start_point, length, angle)
        self.angle = angle
        self.length = length
        self.count_beam = count_beam
        self.pannel_gap = pannel_gap
        self.beam_gap = beam_gap
        self.beam_length = beam_length
        self.beam_width = beam_width
        self.drawing = drawing

    def __repr__(self) -> str:
        return f"Branch(length = {self.length}, angle = {self.angle}, number of beam = {self.count_beam})"

    def __len__(self) -> float:
        return self.length

    def draw_branch(self, filename=None):
        if filename is None:
            filename = "yoshimura_pattern.dxf"
        assert type(filename) == str, "Filename must be a string"

        # Draw the branchs
        length_extremity_lines = (
            self.length
            - self.beam_length * self.count_beam
            - self.beam_gap * (self.count_beam - 1)
        ) / 2
        for angle in (self.angle + 90, self.angle - 90):
            # Draw the extremity line
            start_point_line1 = end_point_of_line(
                self.start_point, self.pannel_gap / 2, angle
            )
            end_point_line1 = end_point_of_line(
                start_point_line1, length_extremity_lines, self.angle
            )
            self.drawing.add(dxf.line(start_point_line1, end_point_line1))

            start_point_line2 = end_point_of_line(
                self.end_point, self.pannel_gap / 2, angle
            )
            end_point_line2 = end_point_of_line(
                start_point_line2, length_extremity_lines, self.angle - 180
            )
            self.drawing.add(dxf.line(start_point_line2, end_point_line2))

            # Draw the beam slots
            start_point_beam = end_point_line1
            for i in range(self.count_beam):
                # left beam slot
                beam_point1 = end_point_of_line(
                    start_point_beam, (self.beam_width - self.pannel_gap) / 2, angle
                )
                beam_point2 = end_point_of_line(
                    beam_point1, self.beam_length, self.angle
                )
                beam_point3 = end_point_of_line(
                    beam_point2, (self.beam_width - self.pannel_gap) / 2, angle + 180
                )
                if i < self.count_beam - 1:
                    beam_point4 = end_point_of_line(
                        beam_point3, self.beam_gap, self.angle
                    )
                    self.drawing.add(
                        dxf.polyline(
                            [
                                start_point_beam,
                                beam_point1,
                                beam_point2,
                                beam_point3,
                                beam_point4,
                            ]
                        )
                    )
                else:
                    self.drawing.add(
                        dxf.polyline(
                            [start_point_beam, beam_point1, beam_point2, beam_point3]
                        )
                    )
                start_point_beam = beam_point4

        self.drawing.save()

    def __call__(self):
        return self.draw_branch()


class BuildingBlockYoshimora:
    def __init__(
        self,
        center: tuple[float],
        radius: float,
        length: float,
        angle: float,
        count_beam: int,
        activated_branch=[True for _ in range(6)],
        pannel_gap=1.2,
        beam_gap=2.33,
        beam_length=6.33,
        beam_width=4.83,
        drawing=dxf.drawing("yoshimura_pattern.dxf"),
    ) -> None:
        self.center = center
        self.radius = radius
        self.length = length
        self.angle = angle
        self.count_beam = count_beam
        self.activated_branch = activated_branch
        self.pannel_gap = pannel_gap
        self.beam_gap = beam_gap
        self.beam_length = beam_length
        self.beam_width = beam_width
        self.drawing = drawing

    def compute_branch_position(self) -> list[tuple[float]]:
        branch_positions = []
        angles = [0, self.angle, 180 - self.angle, 180, 180 + self.angle, -self.angle]
        for angle in angles:
            branch_positions.append(end_point_of_line(self.center, self.radius, angle))
        return branch_positions

    def draw_building_block(self) -> None:
        angles = [0, self.angle, 180 - self.angle, 180, 180 + self.angle, -self.angle]
        branch_positions = self.compute_branch_position()
        for i, branch_state in enumerate(self.activated_branch):
            if branch_state:
                # adapt the length of the branch for the tesselation
                if i == 0 or i == 3:
                    length = (
                        2
                        * math.cos(math.radians(self.angle))
                        * (self.length + 2 * self.radius)
                    ) - 2 * self.radius
                else:
                    length = self.length
                branch = Branch(
                    start_point=branch_positions[i],
                    length=length,
                    angle=angles[i],
                    count_beam=self.count_beam,
                    pannel_gap=self.pannel_gap,
                    beam_gap=self.beam_gap,
                    beam_length=self.beam_length,
                    beam_width=self.beam_width,
                    drawing=self.drawing,
                )
                branch()
            # draw extremity of the branch
            strat_point_extremity1 = end_point_of_line(
                branch_positions[i], self.pannel_gap / 2, angles[i] - 90
            )
            dir_vector1 = normalize_vector(
                vector_difference(self.center, strat_point_extremity1)
            )
            second_point_extremity1 = vector_sum(
                strat_point_extremity1, dir_vector1 * self.radius
            )
            self.drawing.add(dxf.line(strat_point_extremity1, second_point_extremity1))

            strat_point_extremity2 = end_point_of_line(
                branch_positions[i], self.pannel_gap / 2, angles[i] + 90
            )
            dir_vector2 = normalize_vector(
                vector_difference(self.center, strat_point_extremity2)
            )
            second_point_extremity2 = vector_sum(
                strat_point_extremity2, dir_vector2 * self.radius
            )
            self.drawing.add(dxf.line(strat_point_extremity2, second_point_extremity2))
            self.drawing.add(dxf.line(second_point_extremity1, second_point_extremity2))

    def __call__(self) -> None:
        self.draw_building_block()


class YoshimoraTesselation:
    def __init__(
        self,
        size: tuple[int],
        center: tuple[float],
        radius: float,
        length: float,
        angle: float,
        count_beam: int,
        pannel_gap=1.2,
        beam_gap=2.33,
        beam_length=6.33,
        beam_width=4.83,
        drawing=dxf.drawing("yoshimura_pattern.dxf"),
    ) -> None:
        self.size = size
        self.center = center
        self.radius = radius
        self.length = length
        self.angle = angle
        self.count_beam = count_beam
        self.pannel_gap = pannel_gap
        self.beam_gap = beam_gap
        self.beam_length = beam_length
        self.beam_width = beam_width
        self.drawing = drawing

    def compute_activated_branch(self, pos: tuple[int]) -> list[bool]:
        activated_branch = [True for _ in range(6)]
        if pos[0] > 0:
            activated_branch[3] = False
        if pos[1] > 0:
            activated_branch[2] = False
            if pos[0] < self.size[0] - 1:
                activated_branch[1] = False
        return activated_branch

    def compute_branch_position(self, pos: tuple[int]) -> tuple[float]:
        if pos[1] % 2 == 0:
            offset = end_point_of_line(
                (0, 0), 2 * self.radius + self.length, self.angle
            )[0]
        else:
            offset = 0

        vertical_mov = end_point_of_line(
            self.center, pos[1] * (2 * self.radius + self.length), -self.angle
        )
        horizontal_mov = end_point_of_line(
            self.center,
            pos[0]
            * 2
            * math.cos(math.radians(self.angle))
            * (self.length + 2 * self.radius),
            0,
        )

        return horizontal_mov[0] + offset, vertical_mov[1]

    def draw_tesselation(self) -> None:
        assert type(self.size) == tuple, "Size must be a tuple"
        assert len(self.size) == 2, "Size must be a tuple of length 2"
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                center = self.compute_branch_position((i, j))
                activated_branch = self.compute_activated_branch((i, j))
                yoshimora_block = BuildingBlockYoshimora(
                    center=center,
                    radius=self.radius,
                    length=self.length,
                    angle=self.angle,
                    count_beam=self.count_beam,
                    activated_branch=activated_branch,
                    pannel_gap=self.pannel_gap,
                    beam_gap=self.beam_gap,
                    beam_length=self.beam_length,
                    beam_width=self.beam_width,
                    drawing=self.drawing,
                )
                yoshimora_block()

    def __call__(self):
        self.draw_tesselation()


if __name__ == "__main__":
    # branch1 = Branch(
    #     start_point=(0, 0),
    #     length=22,
    #     angle=20,
    #     count_beam=2,
    #     pannel_gap=1.2,
    #     beam_gap=2.33,
    #     beam_length=6.33,
    #     beam_width=4.83,
    # )
    # branch1()
    yoshimora1 = BuildingBlockYoshimora(
        (0, 0), 2, 25, 45, 2, drawing=dxf.drawing("test/yoshimura_pattern.dxf")
    )
    yoshimora2 = BuildingBlockYoshimora(
        (0, 0),
        2,
        25,
        60,
        2,
        [True, True, True, True, True, False],
        drawing=yoshimora1.drawing,
    )
    yoshimora3 = BuildingBlockYoshimora(
        (100, 0),
        2,
        25,
        60,
        2,
        [True, True, True, False, True, False],
        pannel_gap=2,
        drawing=yoshimora1.drawing,
    )
    yoshimora4 = BuildingBlockYoshimora(
        (200, 0),
        2,
        50,
        60,
        3,
        [True, True, True, True, True, True],
        drawing=yoshimora1.drawing,
    )
    # yoshimora1()
    yoshimora2()
    # yoshimora3()
    # yoshimora4()

    tesselation = YoshimoraTesselation(
        center=(0, 0),
        size=(5, 5),
        radius=2,
        length=25,
        angle=60,
        count_beam=2,
        pannel_gap=1.2,
        drawing=dxf.drawing("test/yoshimura_tesselation.dxf"),
    )
    tesselation()
