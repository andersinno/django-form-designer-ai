from django import dispatch

designedform_submit = dispatch.Signal()
designedform_success = dispatch.Signal()
designedform_error = dispatch.Signal()
designedform_render = dispatch.Signal()
