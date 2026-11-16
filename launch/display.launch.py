"""ROS 2: display one hand with RViz and optional joint sliders.

Default model locations: urdf/Lefthand.urdf and urdf/Righthand.urdf.
Legacy SolidWorks mesh package URIs are adapted in memory to meshes/left
and meshes/right in the selected description package.
"""

from pathlib import Path
import xml.etree.ElementTree as ET


def _read_model(model_path, package_share, package_name, check_meshes=True):
    """Read the actual URDF without changing its on-disk contents."""
    model_path = Path(model_path)
    package_share = Path(package_share)
    if not model_path.is_file():
        raise FileNotFoundError(
            f'URDF not found: {model_path}. Install the urdf directory '
            'and rebuild/source the ROS 2 workspace.'
        )

    original = model_path.read_text(encoding='utf-8-sig')
    root = ET.fromstring(original)
    if root.tag != 'robot':
        raise ValueError('Expected a plain URDF with a <robot> root element.')
    links = {link.get('name') for link in root.findall('link')}
    children = {joint.find('child').get('link') for joint in root.findall('joint')}
    roots = links - children
    if len(roots) != 1:
        raise ValueError(f'Expected one root link; found {sorted(roots)}.')

    legacy_prefixes = {
        'package://Lefthand/meshes/': f'package://{package_name}/meshes/left/',
        'package://Righthand/meshes/': f'package://{package_name}/meshes/right/',
    }
    mesh_references = set()
    remapped = 0
    for mesh in root.iter('mesh'):
        filename = mesh.get('filename', '')
        for old, new in legacy_prefixes.items():
            if filename.startswith(old):
                filename = new + filename[len(old):]
                mesh.set('filename', filename)
                remapped += 1
                break
        mesh_references.add(filename)

    if check_meshes:
        own_prefix = f'package://{package_name}/'
        missing = sorted(
            str(package_share / filename[len(own_prefix):])
            for filename in mesh_references
            if filename.startswith(own_prefix)
            and not (package_share / filename[len(own_prefix):]).is_file()
        )
        if missing:
            raise FileNotFoundError(
                'Referenced mesh files are missing from the installed package:\n'
                + '\n'.join(missing)
                + '\nInstall the meshes directory and preserve filename case.'
            )

    movable = [j for j in root.findall('joint') if j.get('type') != 'fixed']
    followers = [j for j in movable if j.find('mimic') is not None]
    information = {
        'root_frame': next(iter(roots)),
        'movable_joints': len(movable),
        'independent_joints': len(movable) - len(followers),
        'mimic_joints': len(followers),
        'remapped_mesh_references': remapped,
    }
    description = '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(
        root, encoding='unicode'
    )
    return description, information


def _launch_setup(context):
    from ament_index_python.packages import get_package_share_directory
    from launch.actions import LogInfo
    from launch.substitutions import LaunchConfiguration
    from launch_ros.actions import Node
    from launch_ros.parameter_descriptions import ParameterValue

    def value(name):
        return LaunchConfiguration(name).perform(context)

    def enabled(name):
        return value(name).lower() == 'true'

    package_name = value('description_package')
    share = Path(get_package_share_directory(package_name))
    model_filename = {'left': 'Lefthand.urdf', 'right': 'Righthand.urdf'}[value('hand')]
    description, information = _read_model(
        share / 'urdf' / model_filename,
        share,
        package_name,
        check_meshes=enabled('check_meshes'),
    )
    use_sim_time = enabled('use_sim_time')
    actions = [
        LogInfo(msg=(
            f"Loaded {model_filename}: {information['independent_joints']} independent "
            f"joints, {information['mimic_joints']} mimic joints; "
            f"root frame: {information['root_frame']}."
        )),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': ParameterValue(description, value_type=str),
                'publish_frequency': 30.0,
                'use_sim_time': use_sim_time,
            }],
        ),
    ]

    if enabled('publish_joint_states'):
        publisher = 'joint_state_publisher_gui' if enabled('gui') else 'joint_state_publisher'
        # Both publishers subscribe to robot_state_publisher's transient-local
        # robot_description topic. Only one joint-state publisher is started.
        actions.append(Node(
            package=publisher,
            executable=publisher,
            name='joint_state_publisher',
            output='screen',
            parameters=[{
                'use_mimic_tags': True,
                'rate': 30,
                'use_sim_time': use_sim_time,
            }],
        ))

    if enabled('rviz'):
        configuration = Path(value('rviz_config'))
        if not configuration.is_absolute():
            configuration = share / configuration
        if not configuration.is_file():
            raise FileNotFoundError(f'RViz configuration not found: {configuration}')
        actions.append(Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', str(configuration)],
            parameters=[{'use_sim_time': use_sim_time}],
        ))
    return actions


def generate_launch_description():
    from launch import LaunchDescription
    from launch.actions import DeclareLaunchArgument, OpaqueFunction

    boolean_options = {'choices': ['true', 'false']}
    return LaunchDescription([
        DeclareLaunchArgument(
            'description_package', default_value='kepler_dexterous_hand_description',
            description='ROS 2 package containing urdf, meshes, launch and rviz.',
        ),
        DeclareLaunchArgument(
            'hand', default_value='left', choices=['left', 'right'],
            description='Select urdf/Lefthand.urdf or urdf/Righthand.urdf.',
        ),
        DeclareLaunchArgument(
            'gui', default_value='true', **boolean_options,
            description='Use sliders; false publishes the initial joint positions.',
        ),
        DeclareLaunchArgument(
            'rviz', default_value='true', **boolean_options,
            description='Start RViz with the supplied display configuration.',
        ),
        DeclareLaunchArgument(
            'publish_joint_states', default_value='true', **boolean_options,
            description='False leaves /joint_states to an external publisher.',
        ),
        DeclareLaunchArgument(
            'use_sim_time', default_value='false', **boolean_options,
            description='Use a simulation clock only when /clock is available.',
        ),
        DeclareLaunchArgument(
            'check_meshes', default_value='true', **boolean_options,
            description='Check mesh paths belonging to the description package.',
        ),
        DeclareLaunchArgument(
            'rviz_config', default_value='rviz/display.rviz',
            description='Absolute path or path relative to the package share directory.',
        ),
        OpaqueFunction(function=_launch_setup),
    ])
