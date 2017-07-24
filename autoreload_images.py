import bpy
import os
from time import time
from bpy.props import BoolProperty, IntProperty, PointerProperty

bl_info = {
    "name": "Image Auto Reload",
    "description": "Automatically reloads any images when they change on disk.",
    "author": "alexandru.pana@manabreakstudios.com",
    "version": (0, 0, 2),
    "blender": (2, 78, 0),
    "location": "3D View > Properties (N)",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}

class ImageAutoReloadPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""

    bl_label = "Image Auto Reload"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        wm = context.window_manager
        
        if not wm.image_autoreload_enabled:
            layout.operator("images.autoreload", text="Enable")
        else:
            layout.operator("images.autoreload", text="Disable")

class ImageAutoReloadOperator(bpy.types.Operator):
    """Auto reload images"""

    bl_idname = "images.autoreload"
    bl_label = "Image Auto Reload Operator"

    timer = None
    
    last_poll = None
    
    def modal(self, context, event):
        
        # Handle stop request
        if not context.window_manager.image_autoreload_enabled:
            ImageAutoReloadOperator.handle_stop(context)
            return {'CANCELLED'}

        # Handle timer events
        if event.type == "TIMER":
            now = time()
            scan_and_reload(self.last_poll)
            self.last_poll = now

        return {'PASS_THROUGH'}

    @staticmethod
    def handle_start(context):
        if not context.window_manager.image_autoreload_enabled:
            context.window_manager.image_autoreload_enabled = True
            ImageAutoReloadOperator.timer = context.window_manager.event_timer_add(1, context.window)
            ImageAutoReloadOperator.last_poll = time()
            print("Started ImageAutoReload")

    @staticmethod
    def handle_stop(context):
        if context.window_manager.image_autoreload_enabled:
            context.window_manager.event_timer_remove(ImageAutoReloadOperator.timer)
            context.window_manager.image_autoreload_enabled = False
            print("Stopped ImageAutoReload")

    def invoke(self, context, event):
        wm = context.window_manager

        if not wm.image_autoreload_enabled:
            ImageAutoReloadOperator.handle_start(context)
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            ImageAutoReloadOperator.handle_stop(context)
            return {'CANCELLED'}
        
def time_since_last_update(image, last_update):
    try:
        return os.lstat(image.filepath_from_user()).st_mtime - last_update
    except:
        return -1

def reload_viewports():
        for area in bpy.context.screen.areas:
            area.tag_redraw()

def scan_and_reload(last_update):
    reload_required = False
    for image in bpy.data.images:
        if image.type == "IMAGE" and time_since_last_update(image, last_update) > 0:
            print("Reloading " + image.name)
            image.reload()
            reload_required = True
    if reload_required:
        reload_viewports()

def register():
    wm = bpy.types.WindowManager
    
    # Runstate initially always set to False
    # note: it is not stored in the Scene, but in window manager:
    wm.image_autoreload_enabled = bpy.props.BoolProperty(default=False)

    bpy.utils.register_module(__name__)
    
def unregister():
    bpy.utils.unregister_module(__name__)
    
    wm = bpy.context.window_manager
    if "image_autoreload_enabled" in wm:
        del wm["image_autoreload_enabled"]


if __name__ == "__main__":
    register()
