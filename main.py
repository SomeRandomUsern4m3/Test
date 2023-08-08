import pyglet
import tools
import wallet
import math
import random
class Game(pyglet.window.Window):
    def __init__(self, w,h,c):
        super(Game, self).__init__(w,h,caption=c, resizable=True)
        pyglet.gl.glClearColor(0.3, 0.8, 0.2,1)
        self.load_game()
        pyglet.app.run()
    def load_batches(self):
        self.menu_batch = pyglet.graphics.Batch()
        self.game_batch = pyglet.graphics.Batch()
    def load_groups(self):
        self.runway_order = pyglet.graphics.Group(order=10)
        self.plane_order = pyglet.graphics.Group(order=12)
        self.gui_order = pyglet.graphics.Group(order=100)
    def load_game(self):
        self.load_batches()
        self.load_groups()
        self.gamestage = "game"
        self.plane_types = ["mini", "jet"]
        self.runways = []
        self.dialog_box = object
        self.taxiways = []
        self.planes = []
        self.money_text = pyglet.text.Label(f'{0}',
                            font_name='Arial',
                            font_size=14,
                            x=10, y=10,
                            anchor_x='left', anchor_y='bottom', batch=self.game_batch, group=self.gui_order)
        self.create_classes()
        pyglet.clock.schedule_interval_soft(self.watch_for_dead_planes, 1/60.00)
        pyglet.clock.schedule_interval_soft(self.update_money_text, 1/60.00)
        #pyglet.clock.schedule_interval_soft(self.kill_dead_dialogs, 1/60.00)
        pyglet.clock.schedule_interval_soft(self.spawn_planes, 1/60.00)
    def update_money_text(self, dt):
        self.money_text.text = f"${wallet.get_wallet_context().money} dollars"
    def watch_for_dead_planes(self, dt):
        for i in self.planes:
            if i.dead:
                self.planes.remove(i)
    #def kill_dead_dialogs(self, dt):
    #    for i in self.dialog_boxes:
    #        if not i == self.dialog_boxes[len(self.dialog_boxes) - 1]:
    #            i.background_sprite = None
    #            i.button = None
    #            self.dialog_boxes.remove(i)
    def spawn_planes(self, dt):
        if random.randint(0, 75) == 49:
            match str(random.randint(1,2)):
                case "1":
                    #taking off plane
                    taxiway = self.taxiways[random.randint(0, len(self.taxiways) - 1)]
                    runway = self.runways[random.randint(0, len(self.runways) - 1)]
                    self.planes.append(Plane(random.randint(taxiway.sprite.x - taxiway.sprite.width//2, taxiway.sprite.x + taxiway.sprite.width // 2), random.randint(taxiway.sprite.y - taxiway.sprite.height//2, taxiway.sprite.y + taxiway.sprite.height//2), random.choice(self.plane_types), "taking_off", runway=runway,batch=self.game_batch, group=self.plane_order))
                case "2":
                    #landing plane
                    runway = self.runways[random.randint(0, len(self.runways) - 1)]
                    self.planes.append(Plane(random.randint(1200, 1200), random.randint(900, 1200), random.choice(self.plane_types), "landing", runway=runway,batch=self.game_batch, group=self.plane_order))
                case _:
                    print("No plane spawned")
    def move_objects(self, x ,y):
        try:
            self.dialog_box.background_sprite.x += x
            self.dialog_box.background_sprite.y += y
            self.dialog_box.button.x += x
            self.dialog_box.button.y += y
            self.dialog_box.button_text.x += x
            self.dialog_box.button_text.y += y
        except AttributeError:
            pass
        for i in self.runways:
            i.sprite.x += x
            i.sprite.y += y
        for i in self.planes:
            i.sprite.x += x
            i.sprite.y += y
            try:
                i.background_gui.x += x
                i.background_gui.y += y
                i.top_bar.x += x
                i.top_bar.y += y
            except AttributeError:
                pass
        for i in self.taxiways:
            i.sprite.x += x
            i.sprite.y += y
    def create_classes(self):
        self.runways.append(Runway(0.7,self.planes, self.game_batch, self.runway_order))
        self.taxiways.append(Taxiway(self.width//2, self.height//2 - 100, self.game_batch, self.runway_order))
        wallet.create_wallet(500)
        #self.planes.append(Plane(50,50,"jet", "landing",self.runways[0], self.game_batch, self.plane_order))
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.move_objects(dx, dy)
    def on_mouse_press(self, x, y, button, modifiers):
        try:
            if tools.separating_axis_theorem(tools.getRect(tools.center_image(pyglet.shapes.Rectangle(x,y,5,5, (0,0,0)))), tools.getRect(self.dialog_box.button)):
                self.dialog_box.target.selected = True
        except AttributeError:
            pass
        for i in self.planes:
            if tools.separating_axis_theorem(tools.getRect(tools.center_image(pyglet.shapes.Rectangle(x,y,5,5, (0,0,0)))), tools.getRect(i.sprite)):
                try:
                    self.dialog_box.background_sprite = None
                    self.dialog_box.button = None
                    self.dialog_box.button_text = None
                except TypeError:
                    pass    
                self.dialog_box = ClickDialog(x,y, i,self.game_batch, self.gui_order)
    def on_draw(self):
        self.clear()
        match self.gamestage:
            case "menu":
                self.menu_batch.draw()
            case "game":
                self.game_batch.draw()
            case _:
                self.clear()
class Plane(object):
    def __init__(self, x=50,y=50,model="jet", type="landing",runway=object, batch=object, group=object):
        """Model is what sprite you want to use eg jet so I type in jet, the type is whether the plane is taking off or landing"""
        self.sprite = pyglet.sprite.Sprite(tools.center_image(pyglet.image.load(f"./Assets/plane_images/{model}_plane.png")), x, y, batch=batch, group=group)
        if type == "taking_off":
            self.background_gui = pyglet.shapes.Rectangle(self.sprite.x, self.sprite.y - (self.sprite.height//2) - 5, 40, 15, (204, 228, 255), batch=batch, group=group)
            self.top_bar = tools.center_image(pyglet.shapes.Rectangle(self.background_gui.x, self.background_gui.y - self.background_gui.height // 2 - 1, 35, 13, (239, 62, 54), batch=batch, group=group))
            self.background_gui.anchor_x = self.background_gui.width//2
            self.background_gui.anchor_y = self.background_gui.height

        self.type = type
        self.dead = False
        self.locked = False #to prevent the lock lose feature being called more than once
        self.success = False
        self.velocity = 0
        self.clock_length = 5
        self.clock_time = self.clock_length

        self.auto_kill_clock = 0
        self.runway_target = runway
        self.selected = False
        match model:
            case "jet":
                self.speed = 150
            case "mini":
                self.speed = 75
            case _:
                self.speed = 75
        self.velocity = self.speed
        if type == "landing":
            pyglet.clock.schedule_interval_soft(self.move_plane, 1/60.00)
        else:
            pyglet.clock.schedule_interval_soft(self.waiting_to_takeoff, 1/60.00)
            pyglet.clock.schedule_interval_soft(self.death_clock, 1)
    def takeoff(self, dt):
        self.sprite.x += self.velocity * math.cos(math.radians(-self.sprite.rotation + 90)) * dt
        self.sprite.y += self.velocity * math.sin(math.radians(-self.sprite.rotation + 90)) * dt
        if not tools.separating_axis_theorem(tools.getRect(self.runway_target.sprite, "left"), tools.getRect(self.sprite)):
            if not self.locked:
                self.locked = True
                self.success = True
                pyglet.clock.schedule_once(self.finish_plane, delay=5)
    def death_clock(self, dt):
        self.top_bar.width -=  7 * dt
        self.clock_time -= 1
        if self.clock_time <= 0:
            self.background_gui = None
            self.top_bar = None
            pyglet.clock.unschedule(self.death_clock)
            self.finish_plane("lose")

    def waiting_to_takeoff(self, dt):
        if self.selected and self.runway_target.runway_free:
            self.sprite.x = self.runway_target.sprite.x + self.runway_target.sprite.width
            self.sprite.y = self.runway_target.sprite.y
            self.sprite.rotation = -self.runway_target.sprite.rotation - 90
            pyglet.clock.unschedule(self.waiting_to_takeoff)
            pyglet.clock.schedule_interval_soft(self.takeoff, 1/60.00)
            pyglet.clock.unschedule(self.death_clock)
            self.clock_time = 10
            self.top_bar = None
            self.background_gui = None
        else:
            self.selected = False
    def finish_plane(self, dt):
        if self.success:
            #add rewards here
            wallet.get_wallet_context().add_money(50)
        else:
            #deduct stuff here
            wallet.get_wallet_context().add_money(-50)
            pass
        #KIIIIIIILLLLLL THHEEEHEHEHEHHEHE PLAAAAAAAAAAAAAAAAAAAAAAAANE
        pyglet.clock.unschedule(self.move_plane)
        pyglet.clock.unschedule(self.land_plane)
        pyglet.clock.unschedule(self.waiting_to_takeoff)
        pyglet.clock.unschedule(self.takeoff)

        self.sprite.batch = None
        self.sprite.group = None
        self.dead = True
        self.runway_target = None
        del self
    def land_plane(self, dt):
        try:
            self.sprite.rotation = self.runway_target.sprite.rotation + 90
            if self.velocity > 0:
                self.velocity  -= self.runway_target.friction
                self.sprite.x += self.velocity * math.cos(math.radians(-self.sprite.rotation + 90)) * dt
                self.sprite.y += self.velocity * math.sin(math.radians(-self.sprite.rotation + 90)) * dt
            else:
                self.velocity = 0
                pyglet.clock.unschedule(self.land_plane)
                self.success = True
                print("fdhafh")
                self.finish_plane(1)
        except AttributeError:
            pyglet.clock.unschedule(self.land_plane)
            
    def move_plane(self, dt):
        self.sprite.x += self.velocity * math.cos(math.radians(-self.sprite.rotation + 90)) * dt
        self.sprite.y += self.velocity * math.sin(math.radians(-self.sprite.rotation + 90)) * dt
        if tools.separating_axis_theorem(tools.getRect(self.runway_target.sprite, "left"), tools.getRect(self.sprite)):
            if self.selected and self.runway_target.runway_free:
                pyglet.clock.unschedule(self.move_plane)
                self.sprite.x = self.runway_target.sprite.x
                self.sprite.y = self.runway_target.sprite.y
                pyglet.clock.schedule_interval_soft(self.land_plane, 1/60.00)
            else:
                self.selected = False
                self.lock = True
        try:
            self.lock
            if not self.locked:
                self.success = False
                pyglet.clock.schedule_once(self.finish_plane, 5)
                self.locked = True
            
        except AttributeError:
            self.sprite.rotation = math.degrees(math.atan2(self.runway_target.sprite.x - self.sprite.x, self.runway_target.sprite.y - self.sprite.y))
class Taxiway(object):
    def __init__(self, x, y, batch, group):
        self.sprite = pyglet.sprite.Sprite(tools.center_image(pyglet.image.load("./Assets/airport_images/taxipad.png")), x=x, y=y, batch=batch, group=group)
class ClickDialog(object):
    def __init__(self, x, y, target, batch, group):
        self.background_sprite = tools.center_image(pyglet.shapes.Rectangle(target.sprite.x ,(target.sprite.y - target.sprite.height // 2) - 70, 100, 100,  (130,115,92), batch=batch, group=group))
        self.button = tools.center_image(pyglet.shapes.Rectangle(self.background_sprite.x, self.background_sprite.y - 35, 80, 20, (156, 222, 159),  batch=batch, group=group))
        if target.type == "landing":
            self.button_text = pyglet.text.Label('Land',
                            font_name='Arial',
                            font_size=14,
                            x=self.button.x, y=self.button.y + 2,
                            anchor_x='center', anchor_y='center', batch=batch, group=group)
        else:
            self.button_text = pyglet.text.Label('Take off',
                            font_name='Arial',
                            font_size=14,
                            x=self.button.x, y=self.button.y + 2,
                            anchor_x='center', anchor_y='center', batch=batch, group=group)
        self.target = target
        self.dead = False
        self.tick = 0
        pyglet.clock.schedule_interval_soft(self.follow_target, 1/60.00)
        pyglet.clock.schedule_interval_soft(self.timeout, 0.5)
    def follow_target(self, dt):
        try:
            if not self.target.selected:
                self.button.color = (156, 222, 159)
            else:
                self.button.color = (255,0,0)
            self.background_sprite.x = self.target.sprite.x
            self.background_sprite.y = (self.target.sprite.y - self.target.sprite.height // 2) - 70
            self.button.x = self.background_sprite.x
            self.button.y = self.background_sprite.y - 35
            self.button_text.x = self.button.x
            self.button_text.y = self.button.y + 2
        except AttributeError:
            pass
    def timeout(self, dt):
        if self.tick > 2:   
            pyglet.clock.unschedule(self.timeout)
            self.background_sprite = None
            self.button = None
            self.button_text = None
            self.dead = True
        self.tick += 1
class Runway(object):
    def __init__(self, friction, planes, batch, group):
        temp_img = pyglet.image.load("./Assets/airport_images/runway.png") #for custom anchor
        temp_img.anchor_y = temp_img.height//2
        self.plane_ref = planes
        self.sprite = pyglet.sprite.Sprite(temp_img, 400 - temp_img.width//2, 450, batch=batch, group=group)
        self.runway_free = True
        self.colls = False
        self.friction = friction
        pyglet.clock.schedule_interval_soft(self.check_if_free, 1/60.00)
    def check_if_free(self, dt):
        for i in self.plane_ref:
            if tools.separating_axis_theorem(tools.getRect(i.sprite), tools.getRect(self.sprite, "left")) and i.selected:
                self.runway_free = False
                self.colls = True
                break
        if not self.colls:
            self.runway_free = True
        self.colls = False
Game(800, 600, "Plane game")