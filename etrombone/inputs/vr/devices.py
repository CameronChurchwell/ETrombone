"""
Get input from OpenXR controllers
"""

import ctypes
import time
import xr


def get_current_time():
    current_time_ns = time.perf_counter_ns()
    current_time_xr = xr.Time(current_time_ns)
    return current_time_xr

def getControllerPosition():
    with xr.InstanceObject(application_name="trombone", enabled_extensions=["XR_MND_headless"]) as instance, \
            xr.SystemObject(instance) as system, \
            xr.SessionObject(system, graphics_binding=None) as session:
            # Set up the controller pose action
            controller_paths = (xr.Path * 2)(
                xr.string_to_path(instance.handle, "/user/hand/left"),
                xr.string_to_path(instance.handle, "/user/hand/right"),
            )
            action_set = xr.create_action_set(
                instance=instance.handle,
                create_info=xr.ActionSetCreateInfo(
                    action_set_name="default_action_set",
                    localized_action_set_name="Default Action Set",
                    priority=0,
                ),
            )
            controller_pose_action = xr.create_action(
                action_set=action_set,
                create_info=xr.ActionCreateInfo(
                    action_type=xr.ActionType.POSE_INPUT,
                    action_name="hand_pose",
                    localized_action_name="Hand Pose",
                    count_subaction_paths=len(controller_paths),
                    subaction_paths=controller_paths,
                ),
            )
            suggested_bindings = (xr.ActionSuggestedBinding * 2)(
                xr.ActionSuggestedBinding(
                    action=controller_pose_action,
                    binding=xr.string_to_path(
                        instance=instance.handle,
                        path_string="/user/hand/left/input/grip/pose",
                    ),
                ),
                xr.ActionSuggestedBinding(
                    action=controller_pose_action,
                    binding=xr.string_to_path(
                        instance=instance.handle,
                        path_string="/user/hand/right/input/grip/pose",
                    ),
                ),
            )
            xr.suggest_interaction_profile_bindings(
                instance=instance.handle,
                suggested_bindings=xr.InteractionProfileSuggestedBinding(
                    interaction_profile=xr.string_to_path(
                        instance.handle,
                        "/interaction_profiles/khr/simple_controller",
                    ),
                    count_suggested_bindings=len(suggested_bindings),
                    suggested_bindings=suggested_bindings,
                ),
            )
            action_spaces = [
                xr.create_action_space(
                    session=session.handle,
                    create_info=xr.ActionSpaceCreateInfo(
                        action=controller_pose_action,
                        subaction_path=controller_paths[0],
                    ),
                ),
                xr.create_action_space(
                    session=session.handle,
                    create_info=xr.ActionSpaceCreateInfo(
                        action=controller_pose_action,
                        subaction_path=controller_paths[1],
                    ),
                ),
            ]
            attach_info = xr.SessionActionSetsAttachInfo(
                count_action_sets=1,
                action_sets=ctypes.pointer(action_set)
            )
            xr.attach_session_action_sets(
                session=session.handle,
                attach_info=attach_info
            )
            # Loop over the render frames
            while True:
                session.poll_xr_events()
                if session.state in (
                    xr.SessionState.READY,
                    xr.SessionState.SYNCHRONIZED,
                    xr.SessionState.VISIBLE,
                    xr.SessionState.FOCUSED,
                ):
                    active_action_set = xr.ActiveActionSet(
                        action_set=action_set,
                        subaction_path=xr.NULL_PATH,
                    )
                    sync_info = xr.ActionsSyncInfo(
                        count_active_action_sets=1,
                        active_action_sets=ctypes.pointer(active_action_set),
                    )
                    xr.sync_actions(
                        session=session.handle,
                        sync_info=sync_info
                    )
                    found_count = 0
                    for index, space in enumerate(action_spaces):
                        current_time = get_current_time()
                        space_location = xr.locate_space(
                            space=space,
                            base_space=session.space.handle,
                            time=current_time
                        )
                        if space_location.location_flags & xr.SPACE_LOCATION_POSITION_VALID_BIT:
                            yield space_location.pose.position.as_numpy()

gen = getControllerPosition()
initial_position = next(gen)

while True:
    try:
        print(next(gen)-initial_position)
        time.sleep(0.5)
    except KeyboardInterrupt:
        print('done')
        break