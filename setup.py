#!/usr/bin/env python3
"""Setup configuration for Omarchy Image Mover."""

from setuptools import setup, find_packages
import os

# Read README if it exists
long_description = 'Interactive theme-based image organizer for Omarchy'
if os.path.exists('README.md'):
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='omarchy-image-mover',
    version='0.0.2',
    description='Interactive theme-based image organizer for Omarchy',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='0xMassi',
    author_email='massimianivalerio1@gmail.com',
    url='https://github.com/0xMassi/omarchy-image-mover',
    packages=find_packages(),
    install_requires=[
        'Pillow>=9.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'omarchy-mover=omarchy_mover.main:main',
            'oim=omarchy_mover.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End esers/Desktop',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.8',
    keywords='image organizer theme wallpaper omarchy',
)
