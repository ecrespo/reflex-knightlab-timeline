import reflex as rx

config = rx.Config(
    app_name="timeline_demo",
    plugins=[
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.SitemapPlugin(),
        rx.plugins.RadixThemesPlugin(),
    ],
)
