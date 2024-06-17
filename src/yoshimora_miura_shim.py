from typing import Any
from dxfwrite import DXFEngine as dxf
from utils import (
    end_point_of_line,
)
import math


class ShimBranch:
    def __init__(
        self,
        position: tuple[float],
        length: float,
        angle: float,
        ratio: float,
        margin: float,
        beam_count: int,
        panel_gap=1.2,
        beam_gap=2.33,
        beam_length=6.33,
        beam_width=4.83,
        drawing=dxf.drawing("yoshimora_branch_shim.dxf"),
        *args,
        **kwargs,
    ) -> None:
        self.position = position
        self.length = length
        self.angle = angle
        self.ratio = ratio
        self.margin = margin
        self.beam_count = beam_count
        self.panel_gap = panel_gap
        self.beam_gap = beam_gap
        self.beam_length = beam_length
        self.beam_width = beam_width
        self.width = self.beam_width * 1 / self.ratio
        self.drawing = drawing

    def __repr__(self) -> str:
        return (
            f"ShimBranch({self.position}, {self.length}, {self.angle}, {self.margin})"
        )

    def _get_extremity_length(self) -> float:
        """Compute the length of the extremity of the shim

        Returns:
            float: length of the extremity of the shim
        """
        return (
            self.length
            - self.beam_length * self.beam_count
            - self.beam_gap * (self.beam_count - 1)
            - self.margin
        ) / 2

    def _get_branch_starting_point(self) -> tuple[float]:
        """Compute the starting point of the branch

        Returns:
            tuple[float]: starting point of the branch
        """
        return end_point_of_line(
            self.position,
            (self.width - self.beam_width + self.panel_gap) / 2,
            self.angle - 90,
        )

    def _get_branch_points(self) -> list[tuple[float]]:
        """Get the points of the branch with the given parameters

        Returns:
            list[tuple[float]]: branch points
        """
        length_extremity_lines = self._get_extremity_length()
        start_point = self._get_branch_starting_point()
        shim_point1 = end_point_of_line(start_point, length_extremity_lines, self.angle)
        shim_point2 = end_point_of_line(
            shim_point1,
            (self.beam_width - self.panel_gap) / 2,
            self.angle - 90,
        )
        shim_point3 = end_point_of_line(shim_point2, self.margin, self.angle)
        shim_point4 = end_point_of_line(shim_point3, self.width, self.angle + 90)
        shim_point5 = end_point_of_line(shim_point4, self.margin, self.angle + 180)
        shim_point6 = end_point_of_line(
            shim_point5,
            (self.beam_width - self.panel_gap) / 2,
            self.angle - 90,
        )
        end_shim = end_point_of_line(
            shim_point6, length_extremity_lines, self.angle - 180
        )
        return (
            start_point,
            shim_point1,
            shim_point2,
            shim_point3,
            shim_point4,
            shim_point5,
            shim_point6,
            end_shim,
        )

    def _draw_branch(self) -> tuple[float]:
        (
            start_point,
            shim_point1,
            shim_point2,
            shim_point3,
            shim_point4,
            shim_point5,
            shim_point6,
            end_shim,
        ) = self._get_branch_points()

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
        self.drawing.save()
        return end_shim

    def __call__(self) -> tuple[float]:
        return self._draw_branch()


class ShimCenterPart:
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
        *args,
        **kwargs,
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
        self.angles = [
            0,
            self.angle,
            180 - self.angle,
            180,
            180 + self.angle,
            -self.angle,
        ]
        self.width = self.beam_width * 1 / self.ratio

    def _get_branch_position(self) -> list[tuple[float]]:
        """Compute the position of the branches of the shim

        Returns:
            list[tuple[float]]: _description_
        """
        branch_positions = []
        for i, angle in enumerate(self.angles):
            point = end_point_of_line(self.center, self.radius, angle)
            for j in range(i):
                if j == 0:
                    point = end_point_of_line(
                        point,
                        (self.beam_width * 1 / self.ratio - self.beam_width) / 2,
                        self.angles[j] + 90,
                    )
                else:
                    point = end_point_of_line(
                        point,
                        self.beam_width * 1 / self.ratio - self.beam_width,
                        self.angles[j] + 90,
                    )
            if i != 0:
                point = end_point_of_line(
                    point,
                    self.panel_gap / 2
                    - (self.width - self.beam_width + self.panel_gap) / 2,
                    self.angles[i] - 90,
                )
            branch_positions.append(point)
        return branch_positions

    def _get_branch_length(self, idx: int) -> float:
        """Compute the length of the branch at the given index

        Args:
            idx (int): index of the branch

        Returns:
            float: length of the branch
        """
        if idx == 0 or idx == 3:
            return (
                2 * math.cos(math.radians(self.angle)) * (self.length + 2 * self.radius)
            ) - 2 * self.radius
        else:
            return self.length

    def _draw_shim(self):
        branch_position = self._get_branch_position()
        for i, branch_state in enumerate(self.activated_branch):
            if branch_state:
                length = self._get_branch_length(i)
                branch = ShimBranch(
                    branch_position[i],
                    length,
                    self.angles[i],
                    self.ratio,
                    self.margin,
                    self.beam_count,
                    self.panel_gap,
                    self.beam_gap,
                    self.beam_length,
                    self.beam_width,
                    self.drawing,
                )
                start_point = branch._get_branch_starting_point()
                if i != 0:
                    self.drawing.add(dxf.line(start_point, end_shim))
                end_shim = branch()  # draw the branch and get the end point
        self.drawing.add(
            dxf.line(
                end_shim,
                end_point_of_line(
                    branch_position[0],
                    (self.width - self.beam_width + self.panel_gap) / 2,
                    self.angles[0] - 90,
                ),
            )
        )  # draw the last join between the branches
        self.drawing.save()

    def __call__(self):
        self._draw_shim()


class ShimSep:
    def __init__(
        self,
        center: tuple[float],
        angle: float,
        ratio: float,
        margin: float,
        panel_gap: 1.2,
        beam_gap: 2.2,
        beam_length=6.33,
        beam_width=4.33,
        drawing=dxf.drawing("yoshimora_shim.dxf"),
        *args,
        **kwargs,
    ):
        self.center = center
        self.angle = angle
        self.ratio = ratio
        self.margin = margin
        self.panel_gap = panel_gap
        self.beam_gap = beam_gap
        self.beam_length = beam_length
        self.beam_width = beam_width
        self.drawing = drawing
        self.width = self.beam_width * 1 / self.ratio

    def _get_seperator_points(self) -> list[tuple[float]]:
        """Get the points of the shim seperator

        Returns:
            list[tuple[float]]: points of the shim seperator
        """
        start_point = end_point_of_line(
            self.center, (self.beam_gap + self.margin) / 2, self.angle + 180
        )
        point1 = end_point_of_line(start_point, self.width / 2, self.angle + 90)
        point2 = end_point_of_line(point1, self.margin, self.angle)
        point3 = end_point_of_line(
            point2, (self.beam_width - self.panel_gap) / 2, self.angle - 90
        )
        point4 = end_point_of_line(point3, self.beam_gap - self.margin, self.angle)
        point5 = end_point_of_line(
            point4, (self.beam_width - self.panel_gap) / 2, self.angle + 90
        )
        point6 = end_point_of_line(point5, self.margin, self.angle)
        point7 = end_point_of_line(point6, self.width, self.angle - 90)
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
        return [
            start_point,
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
        ]

    def _draw_shim_seperator(self) -> None:
        """Draw the shim seperator"""
        points = self._get_seperator_points()[1:]
        points.append(points[0])  # close the loop
        self.drawing.add(dxf.polyline(points))
        self.drawing.save()

    def __call__(self):
        self._draw_shim_seperator()


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
        *args,
        **kwargs,
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
        self.angles = [
            0,
            self.angle,
            180 - self.angle,
            180,
            180 + self.angle,
            -self.angle,
        ]
        self.width = self.beam_width * 1 / self.ratio

    def _get_branch_position(self) -> list[tuple[float]]:
        """Compute the position of the branches of the shim

        Returns:
            list[tuple[float]]: _description_
        """
        branch_positions = []
        for i, angle in enumerate(self.angles):
            point = end_point_of_line(self.center, self.radius, angle)
            for j in range(i):
                if j == 0:
                    point = end_point_of_line(
                        point,
                        (self.beam_width * 1 / self.ratio - self.beam_width) / 2,
                        self.angles[j] + 90,
                    )
                else:
                    point = end_point_of_line(
                        point,
                        self.beam_width * 1 / self.ratio - self.beam_width,
                        self.angles[j] + 90,
                    )
            if i != 0:
                point = end_point_of_line(
                    point,
                    self.panel_gap / 2
                    - (self.width - self.beam_width + self.panel_gap) / 2,
                    self.angles[i] - 90,
                )
            branch_positions.append(point)
        return branch_positions

    def _get_offset_length(self, length) -> float:
        """Compute the offset length of the shim

        Returns:
            float: offset length of the shim
        """
        return (
            (
                length
                - self.beam_length * self.beam_count
                - self.beam_gap * (self.beam_count - 1)
            )
            / 2
            + self.beam_length
            + self.beam_gap / 2
        )

    def _get_branch_length(self, idx: int) -> float:
        """Compute the length of the branch at the given index

        Args:
            idx (int): index of the branch

        Returns:
            float: length of the branch
        """
        if idx == 0 or idx == 3:
            return (
                2 * math.cos(math.radians(self.angle)) * (self.length + 2 * self.radius)
            ) - 2 * self.radius
        else:
            return self.length

    def _get_seperator_center(
        self, idx: int, count: int, offset: float, branch_position: tuple[float]
    ) -> tuple[float]:
        """Compute the center of the shim seperator

        Args:
            count (int): count of the beam
            offset (float): offset of the shim
            branch_position (tuple[float]): position of the branch

        Returns:
            tuple[float]: center of the shim seperator
        """
        return end_point_of_line(
            branch_position,
            offset + count * (self.beam_gap + self.beam_length),
            self.angles[idx],
        )

    def _draw_shim(self) -> None:
        center_shim = ShimCenterPart(
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
        center_shim()  # draw the center part of the shim
        branch_position = center_shim._get_branch_position()
        for i, branch_state in enumerate(self.activated_branch):
            length = self._get_branch_length(i)
            offset = self._get_offset_length(length)
            for count in range(self.beam_count - 1):
                if not branch_state:
                    continue
                center_sep = self._get_seperator_center(
                    i, count, offset, branch_position[i]
                )
                shim_sep = ShimSep(
                    center_sep,
                    self.angles[i],
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
        self._draw_shim()


class ShimTesselation:
    def __init__(
        self,
        size: tuple[int],
        center: tuple[float],
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
        self.center = center
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
        self.width = self.beam_width * 1 / self.ratio
        self.angles = [
            0,
            self.angle,
            180 - self.angle,
            180,
            180 + self.angle,
            -self.angle,
        ]

    def _compute_activated_branch(self, position: tuple[int]) -> list[bool]:
        activated_branch = [True] * 6

        # Deactivate branches based on position
        if position[1] > 0:  # If pos[1] is greater than 0
            activated_branch[3] = False  # Deactivate branch 3
            if position[0] > 0:  # If pos[0] is greater than 0
                activated_branch[2] = False  # Deactivate branch 2

        if (
            position[0] % 2 == 0 and position[1] == 0 and position[0] > 0
        ):  # Special condition for even pos[0] and pos[1] equals 0
            activated_branch[2] = False  # Deactivate branch 2

        if (
            position[1] < self.size[1] - 1 and position[0] > 0
        ):  # If pos[1] is within bounds and pos[0] is greater than 0
            activated_branch[1] = False  # Deactivate branch 1

        if (
            position[1] == self.size[1] - 1 and position[0] % 2 == 1
        ):  # Special condition for pos[1] at upper bound and odd pos[0]
            activated_branch[1] = False  # Deactivate branch 1
        return activated_branch

    def _get_center_position(
        self, branch_number: int, branch_position: tuple[float]
    ) -> tuple[float]:
        point = end_point_of_line(
            branch_position,
            (self.width - self.beam_width + self.panel_gap) / 2,
            self.angles[branch_number] - 90,
        )
        if branch_position == 0:
            point = end_point_of_line(
                point,
                (self.width - self.beam_width + self.panel_gap) / 2,
                self.angles[branch_number] + 90,
            )
        else:
            point = end_point_of_line(
                point,
                self.panel_gap / 2,
                self.angles[branch_number] + 90,
            )
        for i in list(range(0, branch_number))[::-1]:
            if i == 0:
                point = end_point_of_line(
                    point,
                    (self.beam_width * 1 / self.ratio - self.beam_width) / 2,
                    self.angles[i] + 270,
                )
            else:
                point = end_point_of_line(
                    point,
                    self.beam_width * 1 / self.ratio - self.beam_width,
                    self.angles[i] + 270,
                )
        point = end_point_of_line(point, self.radius, self.angles[branch_number] + 180)
        return point

    def _get_new_ref_block(
        self, row_idx: int, old_ref_block: BuildingBlockShimYoshimora
    ) -> tuple[float]:
        if row_idx % 2 == 0:
            branch_position = old_ref_block._get_branch_position()[4]
            new_branch_position = end_point_of_line(
                branch_position,
                old_ref_block._get_branch_length(4),
                old_ref_block.angles[4],
            )
            center = self._get_center_position(1, new_branch_position)
        else:
            branch_position = old_ref_block._get_branch_position()[5]
            new_branch_position = end_point_of_line(
                branch_position,
                old_ref_block._get_branch_length(5),
                old_ref_block.angles[5],
            )
            center = self._get_center_position(2, new_branch_position)

        new_ref = BuildingBlockShimYoshimora(
            center,
            self.radius,
            self.length,
            self.angle,
            self.ratio,
            self.margin,
            self.beam_count,
            self.panel_gap,
            self.beam_gap,
            self._compute_activated_branch((row_idx, 0)),
            self.beam_length,
            self.beam_width,
            self.drawing,
        )
        return new_ref

    def _draw_row(self, row_idx: int, center: tuple[float], size: int):
        for j in range(size):
            activated_branch = self._compute_activated_branch((row_idx, j))
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
            center = end_point_of_line(
                center, buildingBlockShim._get_branch_length(0) + self.radius, 0
            )
            center = self._get_center_position(3, center)

    def _draw_shim_sheet(self) -> None:
        ref_block = BuildingBlockShimYoshimora(
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
        for i in range(self.size[0]):
            self._draw_row(i, ref_block.center, self.size[1])
            ref_block = self._get_new_ref_block(i + 1, ref_block)

    def __call__(self) -> None:
        self._draw_shim_sheet()


if __name__ == "__main__":
    scaling = 1
    pattern_settings = {
        "size": (3, 3),
        "center": (0, 0),
        "ratio": 0.88,
        "radius": 2.5 * scaling,
        "length": 27 * scaling,
        "angle": 40,
        "beam_count": 2,
        "panel_gap": 1.2,
        "beam_gap": 2.33 * scaling,
        "beam_length": 6.33 * scaling,
        "beam_width": 4.83 * scaling,
        "margin": 0.67 * scaling,
        "position": (0, 0),
    }

    shimCenterPart = ShimCenterPart(
        **pattern_settings, drawing=dxf.drawing("test/shim_center_part.dxf")
    )
    shimCenterPart()

    shimSep = ShimSep(**pattern_settings, drawing=dxf.drawing("test/shim_sep.dxf"))
    shimSep.drawing.save()
    shimSep()

    shimBuildingBlock = BuildingBlockShimYoshimora(
        **pattern_settings, drawing=dxf.drawing("test/shim_building_block.dxf")
    )
    shimBuildingBlock()

    shimTesselation = ShimTesselation(
        **pattern_settings,
        drawing=dxf.drawing("out/shim_tesselation.dxf"),
    )
    shimTesselation()
