from typing import Any
from dxfwrite import DXFEngine as dxf
from utils import (
    end_point_of_line,
    normalize_vector,
    vector_difference,
    vector_sum,
    vector_multiply,
)
import math


class CenterShim:
    def __init__(
        self,
        center: tuple[float],
        radius: float,
        length: float,
        angle: float,
        ratio: float,
        margin: float,
        beam_count: int,
        panel_gap: 1.2,
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
        self.beam_count = beam_count
        self.panel_gap = panel_gap
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
            branch_positions.append(point)
        return branch_positions

    def draw_shim(self):
        width = self.beam_width * 1 / self.ratio
        length_extremity_lines = (
            self.length
            - self.beam_length * self.beam_count
            - self.beam_gap * (self.beam_count - 1)
            - self.margin
        ) / 2

        branch_position = self.compute_branch_position()
        angles = [0, self.angle, 180 - self.angle, 180, 180 + self.angle, -self.angle]
        for i, branch_state in enumerate(self.activated_branch):
            if branch_state:
                if i == 0:
                    start_point = end_point_of_line(
                        branch_position[i],
                        (width - self.beam_width + self.panel_gap) / 2,
                        angles[i] - 90,
                    )
                else:
                    start_point = end_point_of_line(
                        branch_position[i],
                        self.panel_gap / 2,
                        angles[i] - 90,
                    )
                    self.drawing.add(dxf.line(start_point, end_shim))
                shim_point1 = end_point_of_line(
                    start_point, length_extremity_lines, angles[i]
                )
                shim_point2 = end_point_of_line(
                    shim_point1,
                    (self.beam_width - self.panel_gap) / 2,
                    angles[i] - 90,
                )
                shim_point3 = end_point_of_line(shim_point2, self.margin, angles[i])
                shim_point4 = end_point_of_line(shim_point3, width, angles[i] + 90)
                shim_point5 = end_point_of_line(
                    shim_point4, self.margin, angles[i] + 180
                )
                shim_point6 = end_point_of_line(
                    shim_point5,
                    (self.beam_width - self.panel_gap) / 2,
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
                    (width - self.beam_width + self.panel_gap) / 2,
                    angles[0] - 90,
                ),
            )
        )
        self.drawing.save()

    def __call__(self):
        self.draw_shim()


class ShimSep:
    def __init__(
        self,
        position: tuple[float],
        angle: float,
        ratio: float,
        margin: float,
        panel_gap: 1.2,
        beam_gap: 2.2,
        beam_length=6.33,
        beam_width=4.33,
        drawing=dxf.drawing("yoshimora_shim.dxf"),
    ):
        self.position = position
        self.angle = angle
        self.ratio = ratio
        self.margin = margin
        self.panel_gap = panel_gap
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
            point2, (self.beam_width - self.panel_gap) / 2, self.angle - 90
        )
        point4 = end_point_of_line(point3, self.beam_gap - self.margin, self.angle)
        point5 = end_point_of_line(
            point4, (self.beam_width - self.panel_gap) / 2, self.angle + 90
        )
        point6 = end_point_of_line(point5, self.margin, self.angle)
        point7 = end_point_of_line(point6, width, self.angle - 90)
        point8 = end_point_of_line(point7, self.margin, self.angle + 180)
        point9 = end_point_of_line(
            point8, (self.beam_width - self.panel_gap) / 2, self.angle + 90
        )
        point10 = end_point_of_line(
            point9, self.beam_gap - self.margin, self.angle + 180
        )
        point11 = end_point_of_line(
            point10, (self.beam_width - self.panel_gap) / 2, self.angle - 90
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


class BuildingBlockShimYoshimora:
    def __init__(
        self,
        center: tuple[float],
        radius: float,
        length: float,
        angle: float,
        ratio: float,
        margin: float,
        beam_count: int,
        panel_gap: 1.2,
        beam_gap: 2.2,
        activated_branch=[True for _ in range(6)],
        beam_length=6.33,
        beam_width=4.33,
        drawing=dxf.drawing("yoshimora_shim.dxf"),
    ) -> None:
        self.center = center
        self.radius = radius
        self.length = length
        self.angle = angle
        self.ratio = ratio
        self.margin = margin
        self.beam_count = beam_count
        self.panel_gap = panel_gap
        self.beam_gap = beam_gap
        self.activated_branch = activated_branch
        self.beam_length = beam_length
        self.beam_width = beam_width
        self.drawing = drawing

    def draw_shim(self) -> None:
        angles = [0, self.angle, 180 - self.angle, 180, 180 + self.angle, -self.angle]
        length_extremity_lines = (
            self.length
            - self.beam_length * self.beam_count
            - self.beam_gap * (self.beam_count - 1)
            - self.margin
        ) / 2
        offset = (self.length - 2 * length_extremity_lines - 2 * self.margin) / (
            self.beam_count
        )
        center_shim = CenterShim(
            self.center,
            self.radius,
            self.length,
            self.angle,
            self.ratio,
            self.margin,
            self.beam_count,
            self.panel_gap,
            self.beam_gap,
            [True for _ in range(6)],
            self.beam_length,
            self.beam_width,
            self.drawing,
        )
        center_shim()
        branch_position = center_shim.compute_branch_position()
        width = self.beam_width * 1 / self.ratio
        for i, branch_state in enumerate(self.activated_branch):
            for count in range(self.beam_count - 1):
                if not branch_state:
                    continue
                if i == 0:
                    position = branch_position[i]
                else:
                    position = end_point_of_line(
                        branch_position[i],
                        self.panel_gap / 2,
                        angles[i] - 90,
                    )
                    position = end_point_of_line(
                        position,
                        (width - self.beam_width + self.panel_gap) / 2,
                        angles[i] + 90,
                    )
                position = end_point_of_line(
                    position,
                    length_extremity_lines
                    + self.margin
                    + offset * (count + 1)
                    - (self.margin + self.beam_gap) / 2,
                    angles[i],
                )
                shim_sep = ShimSep(
                    position,
                    angles[i],
                    self.ratio,
                    self.margin,
                    self.panel_gap,
                    self.beam_gap,
                    self.beam_length,
                    self.beam_width,
                    self.drawing,
                )
                shim_sep()

    def __call__(self):
        self.draw_shim()


class Shim:
    def __init__(
        self,
        size: tuple[int],
        position: tuple[float],
        radius: float,
        length: float,
        angle: float,
        ratio: float,
        margin: float,
        beam_count: int,
        panel_gap=1.2,
        beam_gap=2.33,
        beam_length=6.33,
        beam_width=4.83,
        drawing=dxf.drawing("shim.dxf"),
        *args,
        **kwargs,
    ) -> None:
        self.size = size
        self.position = position
        self.radius = radius
        self.length = length
        self.angle = angle
        self.ratio = ratio
        self.margin = margin
        self.beam_count = beam_count
        self.panel_gap = panel_gap
        self.beam_gap = beam_gap
        self.beam_length = beam_length
        self.beam_width = beam_width
        self.drawing = drawing

    def compute_branch_position(self, center) -> list[tuple[float]]:
        branch_positions = []
        width = self.beam_width * 1 / self.ratio
        angles = [0, self.angle, 180 - self.angle, 180, 180 + self.angle, -self.angle]
        for i, angle in enumerate(angles):
            point = end_point_of_line(center, self.radius, angle)
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
            if i == 0:
                point = end_point_of_line(
                    point,
                    (width - self.beam_width + self.panel_gap) / 2,
                    angles[i] - 90,
                )
            else:
                point = end_point_of_line(point, self.panel_gap / 2, angles[i] - 90)
            point = end_point_of_line(
                point, (width - self.beam_width + self.panel_gap) / 2, angles[i] + 90
            )
            branch_positions.append(point)
        return branch_positions

    def compute_activated_branch(self, pos: tuple[int]) -> list[bool]:
        activated_branch = [True] * 6

        # Deactivate branches based on position
        if pos[1] > 0:  # If pos[1] is greater than 0
            activated_branch[3] = False  # Deactivate branch 3
            if pos[0] > 0:  # If pos[0] is greater than 0
                activated_branch[2] = False  # Deactivate branch 2

        if (
            pos[0] % 2 == 0 and pos[1] == 0 and pos[0] > 0
        ):  # Special condition for even pos[0] and pos[1] equals 0
            activated_branch[2] = False  # Deactivate branch 2

        if (
            pos[1] < self.size[1] - 1 and pos[0] > 0
        ):  # If pos[1] is within bounds and pos[0] is greater than 0
            activated_branch[1] = False  # Deactivate branch 1

        if (
            pos[1] == self.size[1] - 1 and pos[0] % 2 == 1
        ):  # Special condition for pos[1] at upper bound and odd pos[0]
            activated_branch[1] = False  # Deactivate branch 1
        return activated_branch

    def get_center_position(
        self, branch_number: int, branch_position: tuple[float]
    ) -> tuple[float]:
        width = self.beam_width * 1 / self.ratio
        angles = [
            0,
            self.angle,
            180 - self.angle,
            180,
            180 + self.angle,
            -self.angle,
        ]
        point = branch_position
        point = end_point_of_line(
            point,
            (width - self.beam_width + self.panel_gap) / 2,
            angles[branch_number] - 90,
        )
        if branch_position == 0:
            point = end_point_of_line(
                point,
                (width - self.beam_width + self.panel_gap) / 2,
                angles[branch_number] + 90,
            )
        else:
            point = end_point_of_line(
                point,
                self.panel_gap / 2,
                angles[branch_number] + 90,
            )
        for i in list(range(0, branch_number))[::-1]:
            if i == 0:
                point = end_point_of_line(
                    point,
                    (self.beam_width * 1 / self.ratio - self.beam_width) / 2,
                    angles[i] + 270,
                )
            else:
                point = end_point_of_line(
                    point,
                    self.beam_width * 1 / self.ratio - self.beam_width,
                    angles[i] + 270,
                )
        point = end_point_of_line(point, self.radius, angles[branch_number] + 180)
        return point

    def compute_block_position(self, pos: tuple[int]) -> tuple[float]:
        center = self.position
        block_position = end_point_of_line(center, self.radius, 0)
        for i in range(pos[0]):
            branch_position = self.compute_branch_position(center)
            if i % 2 == 0:
                block_position = branch_position[-2]
                block_position = end_point_of_line(
                    block_position, self.length, self.angle + 180
                )
                center = self.get_center_position(1, block_position)
            else:
                block_position = branch_position[-1]
                block_position = end_point_of_line(
                    block_position, self.length, -self.angle
                )
                center = self.get_center_position(2, block_position)

        for _ in range(pos[1]):
            block_position = end_point_of_line(center, self.radius, 0)
            block_position = end_point_of_line(block_position, self.length, 0)
            center = self.get_center_position(3, block_position)
            block_position = end_point_of_line(center, self.radius, 0)
        return [center, block_position]

    def draw_shim_sheet(self) -> None:
        center = self.position
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                center, branch_position = self.compute_block_position((i, j))
                activated_branch = self.compute_activated_branch((i, j))
                buildingBlockShim = BuildingBlockShimYoshimora(
                    center,
                    self.radius,
                    self.length,
                    self.angle,
                    self.ratio,
                    self.margin,
                    self.beam_count,
                    self.panel_gap,
                    self.beam_gap,
                    activated_branch,
                    self.beam_length,
                    self.beam_width,
                    self.drawing,
                )
                buildingBlockShim()

    def __call__(self) -> None:
        self.draw_shim_sheet()


if __name__ == "__main__":
    scaling = 1
    pattern_settings = {
        "size": (3, 3),
        "center": (0, 0),
        "ratio": 0.88,
        "radius": 2 * scaling,
        "length": 25 * scaling,
        "angle": 60,
        "beam_count": 2,
        "panel_gap": 1.2,
        "beam_gap": 2.33 * scaling,
        "beam_length": 6.33 * scaling,
        "beam_width": 4.83 * scaling,
        "margin": 0.67 * scaling,
        "position": (0, 0),
    }
    shimTesselation = Shim(
        **pattern_settings,
        drawing=dxf.drawing("out/shim_tesselation.dxf"),
    )
    shimTesselation()
