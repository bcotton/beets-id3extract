from setuptools import setup

setup(
    name='beets-id3extract',
    version='0.1.0',
    description='Beets plugin to map arbitrary ID3 tags to beets custom fields',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Brian Cotton',
    author_email='bcotton@posteo.net',
    url='https://github.com/your-username/beets-id3extract',
    license='MIT',
    platforms='ALL',
    packages=['beetsplug'],
    install_requires=[
        'beets>=1.6.0',
        'mediafile',
        'mutagen',
    ],
    classifiers=[
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Players :: MP3',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
) 