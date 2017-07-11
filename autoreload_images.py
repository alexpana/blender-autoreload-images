import bpy
import os
from time import time
from bpy.props import BoolProperty, IntProperty, PointerProperty

bl_info = {
    "name": "Image Auto Reload",
    "description": "Automatically reloads any images when they change on disk.",
    "author": "alexandru.pana@manabreakstudios.com",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "3D View > Properties (N)",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}

class ImageAutoReloadSettings(bpy.types.PropertyGroup):
    enabled = BoolProperty(
        name="Enable auto reload",
        description="Enables image auto reloading",
        default = False
    )

class ImageAutoReloadPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""

    bl_label = "Image Auto Reload"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.autoreload_images
        
        layout.prop(props, "enabled", text="Enabled")

class ImageAutoReloadOperator(bpy.types.Operator):
    """Auto reload images"""

    bl_idname = "images.autoreload"
    bl_label = "Image Auto Reload Operator"

    poll_interval = 0.5
    timer = None
    
    _last_poll = None
    
    def modal(self, context, event):
        props = context.scene.autoreload_images
        
        if props.enabled and event.type == "TIMER":
            now = time()
            if self._last_poll is None or now - self._last_poll > self.poll_interval:
                scan_and_reload(self._last_poll or now)
                self._last_poll = now

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.timer = context.window_manager.event_timer_add(0.1, context.window)
        context.window_manager.modal_handler_add(self)
        print("INVOKE")
        return {'RUNNING_MODAL'}
    
def time_since_last_update(image, last_update):
    return os.lstat(image.filepath_from_user()).st_mtime - last_update

def reload_viewports():
        for area in bpy.context.screen.areas:
            area.tag_redraw()

def scan_and_reload(last_update):
    for image in bpy.data.images:
        if image.type == "IMAGE" and time_since_last_update(image, last_update) > 0:
            print("Reloading " + image.name)
            image.reload()
            reload_viewports()

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.autoreload_images = PointerProperty(type=ImageAutoReloadSettings)

def unregister():
    bpy.utils.register_module(__name__)
    del bpy.types.Scene.autoreload_images


if __name__ == "__main__":
    register()
    bpy.ops.images.autoreload('INVOKE_DEFAULT')
