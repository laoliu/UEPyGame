import sys
import unreal as ue

class ControlCamera():
  def __init__(self):

    worlds = ue.all_worlds()
    world = worlds[1]
    controllers = ue.find_all_objects("PlayerController")
    controller = controllers[0]

    self.CameraActors = ue.find_all_objects("CameraActor")

    self.Camera1 = self.CameraActors[0]
    self.Camera2 = self.CameraActors[1]

    print(self.Camera1)
    print(self.Camera2)
    self.MyController = controller
    #self._tick = ue.add_ticker(self.tickfunc, 3)
    self.tickfunc(3)

  def tickfunc(self, d):
    print("xxxx1")
    if (self.MyController):
        if self.Camera2 and self.Camera1:
            if self.Camera2 and self.MyController.get_view_target(0) == self.Camera1:
                print("xxxx3")
                self.MyController.set_view_target_with_blend(self.Camera2, 0, 1) 
                print("xxxx4")
            elif (self.Camera2):
                print("xxxx5")
                self.MyController.set_view_target_with_blend(self.Camera1, 0, 1)   
                print("xxxx6")
        print("xxxx2") 
        #self._tick = ue.add_ticker(self.tickfunc, 3)
    print("yyyy")


ControlCamera()