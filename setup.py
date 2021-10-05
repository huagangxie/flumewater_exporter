import setuptools


setuptools.setup(
    name="flumewater_exporter",
    version="0.0.1",
    author="Huagang Xie",
    author_email="huagangxie@gmail.com",
    packages=setuptools.find_packages(),
    install_requires=[
        "requests>=2.18.4",
        "prometheus_client>=0.2.0",
    ],
    entry_points={
        "console_scripts": [
            "flumewater_exporter = flumewater_exporter:exporter_main",
        ],
    },
)
