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
        drawing=dxf.drawing("yoshimura_branch.dxf"),
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
            filename = "yoshimura_branch.dxf"
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


class BranchTape(Branch):
    def __repr__(self) -> str:
        return f"BranchTape(length = {self.length}, angle = {self.angle}, number of beam = {self.count_beam})"

    def draw_branch(self, filename=None):
        if filename is None:
            filename = "yoshimura_branch.dxf"
        assert type(filename) == str, "Filename must be a string"

        # Draw the branchs
        length_extremity_lines = (
            self.length
            - self.beam_length * self.count_beam
            - self.beam_gap * (self.count_beam - 1)
        ) / 2
        start_point_beam = end_point_of_line(
            self.start_point, length_extremity_lines, self.angle
        )
        start_point_beam = end_point_of_line(
            start_point_beam, self.beam_width / 2, self.angle - 90
        )
        for i in range(self.count_beam):
            # left beam slot
            beam_point1 = end_point_of_line(
                start_point_beam,
                self.beam_width,
                self.angle + 90,
            )
            beam_point2 = end_point_of_line(beam_point1, self.beam_length, self.angle)
            beam_point3 = end_point_of_line(
                beam_point2, self.beam_width, self.angle - 90
            )
            beam_point4 = end_point_of_line(
                beam_point3, self.beam_length, self.angle + 180
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
            start_point_beam = end_point_of_line(
                start_point_beam, self.beam_length + self.beam_gap, self.angle
            )
        self.drawing.save()


class CenterShim:
    def __init__(
        self,
        center: tuple[float],
        radius: float,
        length: float,
        angle: float,
        ratio: float,
        margin: float,
        count_beam: int,
        pannel_gap: 1.2,
        beam_gap: 2.2,
        activated_branch=[True for _ in range(6)],
        beam_length=6.33,
        beam_width=4.33,
        drawing=dxf.drawing("yoshimora_shim.dxf"),
    ):
        self.center = center
        self.radius = radius
        self.length = length
        self.angle = angle
        self.ratio = ratio
        self.margin = margin
        self.count_beam = count_beam
        self.pannel_gap = pannel_gap
        self.beam_gap = beam_gap
        self.activated_branch = activated_branch
        self.beam_length = beam_length
        self.beam_width = beam_width
        self.drawing = drawing

    def compute_branch_position(self) -> list[tuple[float]]:
        branch_positions = []
        angles = [0, self.angle, 180 - self.angle, 180, 180 + self.angle, -self.angle]
        for i, angle in enumerate(angles):
            point = end_point_of_line(self.center, self.radius, angle)
            for j in range(i):
                if j == 0:
                    point = end_point_of_line(
                        point,
                        (self.beam_width * 1 / self.ratio - self.beam_width) / 2,
                        angles[j] + 90,
                    )
                else:
                    point = end_point_of_line(
                        point,
                        self.beam_width * 1 / self.ratio - self.beam_width,
                        angles[j] + 90,
                    )
            # branch_positions.append(end_point_of_line(self.center, self.radius, angle))
            branch_positions.append(point)
        return branch_positions

    def draw_shim(self):
        width = self.beam_width * 1 / self.ratio
        length_extremity_lines = (
            self.length
            - self.beam_length * self.count_beam
            - self.beam_gap * (self.count_beam - 1)
            - self.margin
        ) / 2

        branch_position = self.compute_branch_position()
        angles = [0, self.angle, 180 - self.angle, 180, 180 + self.angle, -self.angle]
        for i, branch_state in enumerate(self.activated_branch):
            if branch_state:
                if i == 0:
                    start_point = end_point_of_line(
                        branch_position[i],
                        (width - self.beam_width + self.pannel_gap) / 2,
                        angles[i] - 90,
                    )
                else:
                    start_point = end_point_of_line(
                        branch_position[i],
                        self.pannel_gap / 2,
                        angles[i] - 90,
                    )
                    self.drawing.add(dxf.line(start_point, end_shim))

                shim_point1 = end_point_of_line(
                    start_point, length_extremity_lines, angles[i]
                )
                shim_point2 = end_point_of_line(
                    shim_point1,
                    (self.beam_width - self.pannel_gap) / 2,
                    angles[i] - 90,
                )
                shim_point3 = end_point_of_line(shim_point2, self.margin, angles[i])
                shim_point4 = end_point_of_line(shim_point3, width, angles[i] + 90)
                shim_point5 = end_point_of_line(
                    shim_point4, self.margin, angles[i] + 180
                )
                shim_point6 = end_point_of_line(
                    shim_point5,
                    (self.beam_width - self.pannel_gap) / 2,
                    angles[i] - 90,
                )
                end_shim = end_point_of_line(
                    shim_point6, length_extremity_lines, angles[i] - 180
                )
                self.drawing.add(
                    dxf.polyline(
                        [
                            start_point,
                            shim_point1,
                            shim_point2,
                            shim_point3,
                            shim_point4,
                            shim_point5,
                            shim_point6,
                            end_shim,
                        ]
                    )
                )
        self.drawing.add(
            dxf.line(
                end_shim,
                end_point_of_line(
                    branch_position[0],
                    (width - self.beam_width + self.pannel_gap) / 2,
                    angles[0] - 90,
                ),
            )
        )
        self.drawing.save()

    def __call__(self):
        self.draw_shim()


class ShimSperator:
    def __init__(
        self,
        position: tuple[float],
        angle: float,
        ratio: float,
        margin: float,
        pannel_gap: 1.2,
        beam_gap: 2.2,
        beam_length=6.33,
        beam_width=4.33,
        drawing=dxf.drawing("yoshimora_shim.dxf"),
    ):
        self.position = position
        self.angle = angle
        self.ratio = ratio
        self.margin = margin
        self.pannel_gap = pannel_gap
        self.beam_gap = beam_gap
        self.beam_length = beam_length
        self.beam_width = beam_width
        self.drawing = drawing

    def draw_shim_seperator(self):
        width = self.beam_width * 1 / self.ratio
        start_point = end_point_of_line(self.position, width / 2, self.angle - 90)
        point1 = end_point_of_line(start_point, width, self.angle + 90)
        point2 = end_point_of_line(point1, self.margin, self.angle)
        point3 = end_point_of_line(
            point2, (self.beam_width - self.pannel_gap) / 2, self.angle - 90
        )
        point4 = end_point_of_line(point3, self.beam_gap - self.margin, self.angle)
        point5 = end_point_of_line(
            point4, (self.beam_width - self.pannel_gap) / 2, self.angle + 90
        )
        point6 = end_point_of_line(point5, self.margin, self.angle)
        point7 = end_point_of_line(point6, width, self.angle - 90)
        point8 = end_point_of_line(point7, self.margin, self.angle + 180)
        point9 = end_point_of_line(
            point8, (self.beam_width - self.pannel_gap) / 2, self.angle + 90
        )
        point10 = end_point_of_line(
            point9, self.beam_gap - self.margin, self.angle + 180
        )
        point11 = end_point_of_line(
            point10, (self.beam_width - self.pannel_gap) / 2, self.angle - 90
        )
        point12 = end_point_of_line(point11, self.margin, self.angle + 180)
        self.drawing.add(
            dxf.polyline(
                [
                    point1,
                    point2,
                    point3,
                    point4,
                    point5,
                    point6,
                    point7,
                    point8,
                    point9,
                    point10,
                    point11,
                    point12,
                    point1,
                ]
            )
        )
        self.drawing.save()

    def __call__(self):
        self.draw_shim_seperator()


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
        tape=False,
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
        self.tape = tape

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
                if not self.tape:
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
                else:
                    branch = BranchTape(
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
            if not self.tape:
                strat_point_extremity1 = end_point_of_line(
                    branch_positions[i], self.pannel_gap / 2, angles[i] - 90
                )
                dir_vector1 = normalize_vector(
                    vector_difference(self.center, strat_point_extremity1)
                )
                second_point_extremity1 = vector_sum(
                    strat_point_extremity1, dir_vector1 * self.radius
                )
                self.drawing.add(
                    dxf.line(strat_point_extremity1, second_point_extremity1)
                )

                strat_point_extremity2 = end_point_of_line(
                    branch_positions[i], self.pannel_gap / 2, angles[i] + 90
                )
                dir_vector2 = normalize_vector(
                    vector_difference(self.center, strat_point_extremity2)
                )
                second_point_extremity2 = vector_sum(
                    strat_point_extremity2, dir_vector2 * self.radius
                )
                self.drawing.add(
                    dxf.line(strat_point_extremity2, second_point_extremity2)
                )
                self.drawing.add(
                    dxf.line(second_point_extremity1, second_point_extremity2)
                )

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
        tape=False,
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
        self.tape = tape

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
                    tape=self.tape,
                )
                yoshimora_block()

    def __call__(self):
        self.draw_tesselation()


class BuildingBlockShim:
    def __init__(
        self,
        start_point: tuple[float],
        length: float,
        angle: float,
        activated_branch=[True for _ in range(3)],
        beam_gap=2.33,
        beam_length=6.33,
        beam_width=4.83,
        drawing=dxf.drawing("yoshimura_shim.dxf"),
    ):
        pass


if __name__ == "__main__":
    # tesselation = YoshimoraTesselation(
    #     center=(0, 0),
    #     size=(5, 5),
    #     radius=2,
    #     length=25,
    #     angle=60,
    #     count_beam=2,
    #     pannel_gap=1.2,
    #     drawing=dxf.drawing("test/yoshimura_tesselation.dxf"),
    # )
    # tesselation()

    # tesselation_tape = YoshimoraTesselation(
    #     center=(200, 0),
    #     size=(5, 5),
    #     radius=2,
    #     length=25,
    #     angle=60,
    #     count_beam=2,
    #     pannel_gap=1.2,
    #     drawing=tesselation.drawing,
    #     tape=True,
    # )
    # tesselation_tape()
    activated_branch = [True for _ in range(6)]
    activated_branch[0] = True
    center_shim = CenterShim(
        (0, 0),
        2,
        25,
        44,
        0.88,
        0.67,
        2,
        1.2,
        2.3,
        beam_width=4.83,
        beam_length=6.33,
        activated_branch=activated_branch,
        drawing=dxf.drawing("test/shim.dxf"),
    )
    center_shim()

    sep_shim = ShimSperator(
        (20, 0), 0, 0.88, 0.67, 1.2, 2.33, beam_width=4.83, drawing=center_shim.drawing
    )
    sep_shim()
