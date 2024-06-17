from typing import Any
from dxfwrite import DXFEngine as dxf
import math
from utils import (
    end_point_of_line,
    normalize_vector,
    vector_difference,
    vector_sum,
    vector_multiply,
)


class Branch:
    def __init__(
        self,
        position: tuple[float],
        length: float,
        angle: float,
        beam_count: int,
        panel_gap=1.2,
        beam_gap=2.33,
        beam_length=6.33,
        beam_width=4.83,
        drawing=dxf.drawing("yoshimura_branch.dxf"),
    ) -> None:
        self.position = position
        self.end_point = end_point_of_line(self.position, length, angle)
        self.angle = angle
        self.length = length
        self.beam_count = beam_count
        self.panel_gap = panel_gap
        self.beam_gap = beam_gap
        self.beam_length = beam_length
        self.beam_width = beam_width
        self.drawing = drawing

    def __repr__(self) -> str:
        return f"Branch(length = {self.length}, angle = {self.angle}, number of beam = {self.beam_count})"

    def __len__(self) -> float:
        return self.length

    def _get_extremity_length(self) -> float:
        """Compute the length of the extremity line of the branch

        Returns:
            float: length of the extremity line
        """
        return (
            self.length
            - self.beam_length * self.beam_count
            - self.beam_gap * (self.beam_count - 1)
        ) / 2

    def _draw_extremity_line(self, angle: float, extremity_length: float) -> None:
        """Draw the extremity line of the branch with the given parameters

        Args:
            angle (float): angle of the extremity line (self.angle + 90 or self.angle - 90) depending on the side
            extremity_length (float): length of the extremity line
        """
        # draw the first extremity line
        start_point = end_point_of_line(
            self.position, self.panel_gap / 2, angle
        )  # going on the good side of the branch
        end_point = end_point_of_line(start_point, extremity_length, self.angle)
        self.drawing.add(dxf.line(start_point, end_point))

        # draw the second extremity line
        start_point = end_point_of_line(
            self.end_point, self.panel_gap / 2, angle
        )  # going on the good side of the branch
        end_point = end_point_of_line(start_point, extremity_length, self.angle - 180)
        self.drawing.add(dxf.line(start_point, end_point))

    def _get_beam_starting_point(
        self, angle: float, extremity_length: float
    ) -> tuple[float]:
        """Compute the starting point of the beam unit of the branch with the given parameters

        Args:
            angle (float): angle of the beam (self.angle + 90 or self.angle - 90) depending on the side
            extremity_length (float): length of the extremity line

        Returns:
            tuple[float]: starting point of the beam unit
        """
        start_point = end_point_of_line(self.position, self.panel_gap / 2, angle)
        return end_point_of_line(start_point, extremity_length, self.angle)

    def _get_beam_points(
        self, start_point: tuple[float], angle: float
    ) -> tuple[tuple[float]]:
        """Get the points of the beam unit of the branch with the given parameters

        Args:
            start_point (tuple[float]): starting point of the beam
            angle (float): angle of the beam (self.angle + 90 or self.angle - 90) depending on the side

        Returns:
            tuple[tuple[float]]: differents points of the beam unit
        """
        beam_point1 = end_point_of_line(
            start_point,
            (self.beam_width - self.panel_gap) / 2,
            angle,
        )
        beam_point2 = end_point_of_line(beam_point1, self.beam_length, self.angle)
        beam_point3 = end_point_of_line(
            beam_point2,
            (self.beam_width - self.panel_gap) / 2,
            angle + 180,
        )
        return beam_point1, beam_point2, beam_point3

    def _draw_beam(
        self, start_point_beam: tuple[float], angle: float, i: int
    ) -> tuple[float]:
        """Draw a beam unit of the branch with the given parameters

        Args:
            start_point_beam (tuple[float]): starting point of the beam
            angle (float): angle of the beam (self.angle + 90 or self.angle - 90) depending on the side
            i (int): beam count index

        Returns:
            tuple[float]: end point of the beam unit if not the last one
        """
        beam_point1, beam_point2, beam_point3 = self._get_beam_points(
            start_point_beam, angle
        )
        if i < self.beam_count - 1:
            beam_point4 = end_point_of_line(beam_point3, self.beam_gap, self.angle)
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
            return beam_point4
        else:
            self.drawing.add(
                dxf.polyline([start_point_beam, beam_point1, beam_point2, beam_point3])
            )

    def _draw_branch(self):
        """Draw the branch with the given parameters"""
        length_extremity_lines = self._get_extremity_length()
        for angle in (self.angle + 90, self.angle - 90):
            self._draw_extremity_line(angle, length_extremity_lines)
            start_point_beam = self._get_beam_starting_point(
                angle, length_extremity_lines
            )
            for i in range(self.beam_count):
                end_point_beam = self._draw_beam(start_point_beam, angle, i)
                start_point_beam = end_point_beam

        self.drawing.save()

    def __call__(self):
        return self._draw_branch()


class BranchTape(Branch):
    def __repr__(self) -> str:
        return f"BranchTape(length = {self.length}, angle = {self.angle}, number of beam = {self.beam_count})"

    def _get_beam_starting_point(self, extremity_length: float) -> tuple[float]:
        """Compute the starting point of the beam unit of the branch with the given parameters

        Args:
            extremity_length (float): length of the extremity line

        Returns:
            tuple[float]: starting point of the beam unit
        """
        start_point = end_point_of_line(
            self.position, self.beam_width / 2, self.angle - 90
        )
        return end_point_of_line(start_point, extremity_length, self.angle)

    def _get_beam_points(self, start_point_beam: tuple[float]) -> tuple[tuple[float]]:
        """Compute the points of the beam unit of the branch with the given parameters

        Args:
            start_point_beam (tuple[float]): starting point of the beam

        Returns:
            tuple[tuple[float]]: differents points of the beam unit
        """
        beam_point1 = end_point_of_line(
            start_point_beam, self.beam_width, self.angle + 90
        )
        beam_point2 = end_point_of_line(beam_point1, self.beam_length, self.angle)
        beam_point3 = end_point_of_line(beam_point2, self.beam_width, self.angle - 90)
        beam_point4 = end_point_of_line(beam_point3, self.beam_length, self.angle + 180)
        return beam_point1, beam_point2, beam_point3, beam_point4

    def _draw_branch(self):
        length_extremity_lines = self._get_extremity_length()
        start_point_beam = self._get_beam_starting_point(length_extremity_lines)
        for _ in range(self.beam_count):
            beam_point1, beam_point2, beam_point3, beam_point4 = self._get_beam_points(
                start_point_beam
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


class BuildingBlockYoshimora:
    def __init__(
        self,
        center: tuple[float],
        radius: float,
        length: float,
        angle: float,
        beam_count: int,
        activated_branch=[True for _ in range(6)],
        panel_gap=1.2,
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
        self.beam_count = beam_count
        self.activated_branch = activated_branch
        self.panel_gap = panel_gap
        self.beam_gap = beam_gap
        self.beam_length = beam_length
        self.beam_width = beam_width
        self.drawing = drawing
        self.tape = tape
        self.angles = [
            0,
            self.angle,
            180 - self.angle,
            180,
            180 + self.angle,
            -self.angle,
        ]

    def _compute_branch_position(self) -> list[tuple[float]]:
        """Compute the position of the branches

        Returns:
            list[tuple[float]]: list of the position of the branches in the order of the angles
        """
        branch_positions = []
        for angle in self.angles:
            branch_positions.append(end_point_of_line(self.center, self.radius, angle))
        return branch_positions

    def _get_horizontal_branch_length(self) -> float:
        """Compute the length of the horizontal branch of the building block

        Returns:
            float: length of the horizontal branch
        """
        return (
            2 * math.cos(math.radians(self.angle)) * (self.length + 2 * self.radius)
        ) - 2 * self.radius

    def _create_branch(
        self, position: tuple[float], length: float, angle: float
    ) -> Any:
        """Create a branch or a tape branch depending on the tape attribute

        Args:
            position (tuple[float]): position of the branch
            length (float): length of the branch (depending of the branch position in the building block)
            angle (float): angle of the branch

        Returns:
            Any: branch or tape branch object
        """
        if not self.tape:
            return Branch(
                position=position,
                length=length,
                angle=angle,
                beam_count=self.beam_count,
                panel_gap=self.panel_gap,
                beam_gap=self.beam_gap,
                beam_length=self.beam_length,
                beam_width=self.beam_width,
                drawing=self.drawing,
            )
        else:
            return BranchTape(
                position=position,
                length=length,
                angle=angle,
                beam_count=self.beam_count,
                panel_gap=self.panel_gap,
                beam_gap=self.beam_gap,
                beam_length=self.beam_length,
                beam_width=self.beam_width,
                drawing=self.drawing,
            )

    def _draw_branch_center_support(self, position: tuple[float], angle: float) -> None:
        """Draw the center support of the branch useful for the manufacturing

        Args:
            position (tuple[float]): position of the branch
            angle (float): angle of the branch
        """
        start_point_extremity1 = end_point_of_line(
            position, self.panel_gap / 2, angle - 90
        )
        dir_vector1 = normalize_vector(
            vector_difference(self.center, start_point_extremity1)
        )
        second_point_extremity1 = vector_sum(
            start_point_extremity1,
            vector_multiply(dir_vector1, self.radius / 2),
        )
        self.drawing.add(dxf.line(start_point_extremity1, second_point_extremity1))

        start_point_extremity2 = end_point_of_line(
            position, self.panel_gap / 2, angle + 90
        )
        dir_vector2 = normalize_vector(
            vector_difference(self.center, start_point_extremity2)
        )
        second_point_extremity2 = vector_sum(
            start_point_extremity2,
            vector_multiply(dir_vector2, self.radius / 2),
        )
        self.drawing.add(dxf.line(start_point_extremity2, second_point_extremity2))
        self.drawing.add(dxf.line(second_point_extremity1, second_point_extremity2))
        self.drawing.save()

    def _draw_building_block(self) -> None:
        """Draw the building block with the given parameters"""
        branch_positions = self._compute_branch_position()
        for i, branch_state in enumerate(self.activated_branch):
            if branch_state:  # branch is activated
                # adapt the length of the branch for the tesselation
                if i == 0 or i == 3:
                    length = self._get_horizontal_branch_length()
                else:
                    length = self.length
                branch = self._create_branch(
                    branch_positions[i], length, self.angles[i]
                )  # create the i-th branch
                branch()  # draw the branch

            if not self.tape:
                self._draw_branch_center_support(
                    branch_positions[i], self.angles[i]
                )  # draw the center support

    def __call__(self) -> None:
        self._draw_building_block()


class YoshimoraTesselation:
    def __init__(
        self,
        size: tuple[int],
        center: tuple[float],
        radius: float,
        length: float,
        angle: float,
        beam_count: int,
        panel_gap=1.2,
        beam_gap=2.33,
        beam_length=6.33,
        beam_width=4.83,
        drawing=dxf.drawing("yoshimura_pattern.dxf"),
        tape=False,
        *args,
        **kwargs,
    ) -> None:
        """Create a Yoshimora Tesselation

        Args:
            size (tuple[int]): size of the tesselation (number of building blocks in x and y)
            center (tuple[float]): center of the (0,0) building block
            radius (float): radius of the building block
            length (float): regular length of the branch
            angle (float): angle of the branch
            beam_count (int): number of beam in the branch
            panel_gap (float, optional): gap between the panels (Defaults to 1.2)
            beam_gap (float, optional): gap between beams in a branch (Defaults to 2.33)
            beam_length (float, optional): beam length (Defaults to 6.33, see README for more schematic)
            beam_width (float, optional): beam width (Defaults to 4.83, see README for more schematic)
            drawing (_type_, optional): dxf object (Defaults to dxf.drawing("yoshimura_pattern.dxf"))
            tape (bool, optional): tape tesselation or not (Defaults to False)
        """
        assert (type(size) == tuple) and (
            len(size) == 2
        ), "Size must be a tuple of 2 integers"
        self.size = size
        self.center = center
        self.radius = radius
        self.length = length
        self.angle = angle
        self.beam_count = beam_count
        self.panel_gap = panel_gap
        self.beam_gap = beam_gap
        self.beam_length = beam_length
        self.beam_width = beam_width
        self.drawing = drawing
        self.tape = tape

    def _get_activated_branch(self, position: tuple[int]) -> list[bool]:
        """Choose which branch to activate based on the position of the building block to avoid overlapping

        Args:
            center (tuple[int]): coordinates (index) of the building block

        Returns:
            list[bool]: list of the activated branches
        """
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

    def _get_block_center(self, position: tuple[int]) -> tuple[float]:
        """Compute the center of the building block based on its position

        Args:
            position (tuple[int]): coordinates (index) of the building block

        Returns:
            tuple[float]: center of the building block
        """
        if position[0] % 2 == 0:
            offset = end_point_of_line(
                (0, 0), 2 * self.radius + self.length, self.angle
            )[0]
        else:
            offset = 0

        vertical_mov = end_point_of_line(
            self.center, position[0] * (2 * self.radius + self.length), -self.angle
        )
        horizontal_mov = end_point_of_line(
            self.center,
            position[1]
            * 2
            * math.cos(math.radians(self.angle))
            * (self.length + 2 * self.radius),
            0,
        )
        return horizontal_mov[0] + offset, vertical_mov[1]

    def _draw_tesselation(self) -> None:
        """Draw the tesselation given the parameters"""
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                center = self._get_block_center((i, j))
                activated_branch = self._get_activated_branch((i, j))
                yoshimora_block = BuildingBlockYoshimora(
                    center=center,
                    radius=self.radius,
                    length=self.length,
                    angle=self.angle,
                    beam_count=self.beam_count,
                    activated_branch=activated_branch,
                    panel_gap=self.panel_gap,
                    beam_gap=self.beam_gap,
                    beam_length=self.beam_length,
                    beam_width=self.beam_width,
                    drawing=self.drawing,
                    tape=self.tape,
                )
                yoshimora_block()

    def __call__(self):
        self._draw_tesselation()


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
    tesselation = YoshimoraTesselation(
        **pattern_settings,
        drawing=dxf.drawing("out/yoshimura_tesselation.dxf"),
    )
    tesselation()

    tesselationTape = YoshimoraTesselation(
        **pattern_settings,
        drawing=dxf.drawing("out/yoshimura_tesselation_tape.dxf"),
        tape=True,
    )
    tesselationTape()
