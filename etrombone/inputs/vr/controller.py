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

def getControllerState():
    with xr.InstanceObject(application_name="trombone", enabled_extensions=["XR_MND_headless"]) as instance, \
            xr.SystemObject(instance) as system, \
            xr.SessionObject(system, graphics_binding=None) as session:
        # Set up the controller pose action

        right_controller_path = xr.string_to_path(instance.handle, "/user/hand/right")

        trombone_slide_action_set = xr.create_action_set(
            instance=instance.handle,
            create_info=xr.ActionSetCreateInfo(
                action_set_name="trombone_slide",
                localized_action_set_name="Trombone Slide",
                priority=0,
            ),
        )

        slide_position_action = xr.create_action(
            action_set=trombone_slide_action_set,
            create_info=xr.ActionCreateInfo(
                action_type=xr.ActionType.POSE_INPUT,
                action_name="slide_position",
                localized_action_name="Slide Position",
                count_subaction_paths=1,
                subaction_paths=right_controller_path
            ),
        )

        calibration_action = xr.create_action(
            action_set=trombone_slide_action_set,
            create_info=xr.ActionCreateInfo(
                action_type=xr.ActionType.BOOLEAN_INPUT,
                action_name='slide_calibrate_button',
                localized_action_name='Slide Calibration Button',
                count_subaction_paths=1,
                subaction_paths=right_controller_path
            )
        )

        suggested_bindings = (xr.ActionSuggestedBinding * 2)(
            xr.ActionSuggestedBinding(
                action=slide_position_action,
                binding=xr.string_to_path(
                    instance=instance.handle,
                    path_string="/user/hand/right/input/grip/pose",
                ),
            ),
            xr.ActionSuggestedBinding(
                action=calibration_action,
                binding=xr.string_to_path(
                    instance=instance.handle,
                    path_string="/user/hand/right/input/a/click",
                ),
            ),
        )

        xr.suggest_interaction_profile_bindings(
            instance=instance.handle,
            suggested_bindings=xr.InteractionProfileSuggestedBinding(
                interaction_profile=xr.string_to_path(
                    instance.handle,
                    "/interaction_profiles/valve/index_controller",
                ),
                count_suggested_bindings=len(suggested_bindings),
                suggested_bindings=suggested_bindings,
            ),
        )

        action_spaces = [
            xr.create_action_space(
                session=session.handle,
                create_info=xr.ActionSpaceCreateInfo(
                    action=slide_position_action,
                    subaction_path=right_controller_path,
                ),
            ),
        ]

        attach_info = xr.SessionActionSetsAttachInfo(
            count_action_sets=1,
            action_sets=ctypes.pointer(trombone_slide_action_set)
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
                    action_set=trombone_slide_action_set,
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
                for space in action_spaces:
                    current_time = get_current_time()
                    slide_state = {}

                    #get location
                    space_location = xr.locate_space(
                        space=space,
                        base_space=session.space.handle,
                        time=current_time
                    )
                    if space_location.location_flags & xr.SPACE_LOCATION_POSITION_VALID_BIT:
                        slide_state['position'] = space_location.pose.position.as_numpy()
                    
                    slide_state['calibrate'] = xr.get_action_state_boolean(
                        session=session.handle,
                        get_info=xr.ActionStateGetInfo(
                            action=calibration_action,
                        )
                    ).current_state

                    yield slide_state


if __name__ == '__main__':
    gen = getControllerState()
    while 'position' not in next(gen):
        pass
    initial_state = next(gen)
    while True:
        try:
            current_state = next(gen)
            print(current_state['position']-initial_state['position'])
            print(current_state['calibrate'])
            time.sleep(0.5)
        except KeyboardInterrupt:
            print('done')
            break