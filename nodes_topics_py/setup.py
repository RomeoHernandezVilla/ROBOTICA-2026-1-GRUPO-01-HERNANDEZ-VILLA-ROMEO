from setuptools import find_packages, setup

package_name = 'nodes_topics_py'

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
    maintainer='robousr',
    maintainer_email='erik.pena@ingenieria.unam.edu',
    description='TODO: Package description',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
          'my_node_py = nodes_topics_py.mi_primer_nodo:main',
          'publish2_node_py = nodes_topics_py.publish_node:main',
          'subcriber_node_py = nodes_topics_py.sub_node:main'
        ],
    },
)
