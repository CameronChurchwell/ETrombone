import xr

def getContext():
    context = xr.ContextObject(
        instance_create_info=xr.InstanceCreateInfo(
            enabled_extension_names=[
                xr.KHR_OPENGL_ENABLE_EXTENSION_NAME,
            ],
        ),
    )
    return context
