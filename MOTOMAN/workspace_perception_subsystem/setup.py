from setuptools import find_packages, setup

package_name = 'workspace_perception_subsystem'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rsdlab',
    maintainer_email='rsdlab@todo.todo',
    description='This package is licensed under the MIT License.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'WSRecognizeModule = workspace_perception_subsystem.WSRecognizeModule:main',
        ],
    },
)