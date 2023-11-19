import svgwrite


class SvgDrawer:
    width = 500
    height = 400

    background_color = "#1a1b27"
    background_radius = 12

    x, y = 20, 40
    font_height = 36
    font_size = 18
    circle_r = 8
    font = (
        '"Helvetica Neue", '
        "Helvetica,"
        '"Microsoft Yahei", '
        "Arial, "
        '"Hiragino Sans GB", '
        '"Heiti SC", '
        '"WenQuanYi Micro Hei", '
        "sans-serif"
    )
    font_weight = "800"
    text_color = "#38bdae"

    def __init__(self, data):
        self.dwg = svgwrite.Drawing(
            "status.svg", profile="tiny", size=(self.width, self.height)
        )

        background = self.dwg.rect(
            insert=(0, 0),
            size=(self.width, self.height),
            rx=self.background_radius,
            ry=self.background_radius,
            fill=self.background_color,
        )
        self.dwg.add(background)

        self.data = data
        self.projects = data["projects"]
        self.project_count = len(self.projects)
        self.left_count = (self.project_count + 1) // 2

    @staticmethod
    def get_project_info(project: dict) -> (str, str):
        """获取项目名称和状态"""
        name = project["name"]
        total_count = project["total_count"]
        healthy_count = project["healthy_count"]
        if total_count == healthy_count:
            status_color = "green"
        elif healthy_count > 0:
            status_color = "yellow"
        else:
            status_color = "red"

        return name, status_color

    def draw_project(self, project: dict, x: int, y: int):
        name, color = self.get_project_info(project)
        text = self.dwg.text(
            name,
            insert=(x, y),
            fill=self.text_color,
            font_size=self.font_size,
            font_family=self.font,
            font_weight=self.font_weight,
        )
        self.dwg.add(text)

        circle = self.dwg.circle(
            center=(x + 180, y - self.circle_r // 2),
            r=self.circle_r,
            fill=color,
        )
        self.dwg.add(circle)

    def draw(self):
        for left_index in range(self.left_count):
            # 左侧项目
            self.draw_project(self.projects[left_index], self.x, self.y)

            # 右侧项目
            if left_index + self.left_count < self.project_count:
                self.draw_project(
                    self.projects[left_index + self.left_count],
                    self.x + self.width // 2,
                    self.y,
                )

            # 更新y坐标
            self.y += self.font_height

        # 绘制服务器数量
        x, y = 20, self.height - 2 * self.font_height
        self.dwg.add(
            self.dwg.text(
                f"服务器数量: {self.data['host_count']}",
                insert=(x, y),
                fill=self.text_color,
                font_size=self.font_size,
                font_family=self.font,
                font_weight=self.font_weight,
            )
        )

        # 绘制更新时间
        x, y = 20, self.height - 1 * self.font_height

        self.dwg.add(
            self.dwg.text(
                f"更新时间: {self.data['time'].strftime('%Y-%m-%d %H:%M:%S')}",
                insert=(x, y),
                fill=self.text_color,
                font_size=self.font_size,
                font_family=self.font,
                font_weight=self.font_weight,
            )
        )

        return self.dwg.tostring()
