# -*- coding: utf-8 -*-


from flet import *


def get_logo():
    return Container(
        height=100,
        margin=0,
        padding=padding.symmetric(horizontal=20),
        bgcolor="#6B3CF0",
        border_radius=0,
        expand=False,
        shadow=BoxShadow(
            blur_radius=15,
            color="#00000020",
            offset=Offset(0, 3),
            spread_radius=1
        ),
        content=Row(
            spacing=15,
            vertical_alignment="center",
            controls=[
                Container(
                    width=60,
                    height=60,
                    border_radius=10,
                    bgcolor="white",
                    alignment=alignment.center,
                    content=Icon(
                        name=Icons.BOLT_ROUNDED,
                        size=28,
                        color="#6B3CF0"
                    )
                ), Text("Zepix",size=28,weight=FontWeight.BOLD,color="white")
              
            ]
        )
    )
