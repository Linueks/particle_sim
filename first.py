import pygame
import numpy as np


class Object:
    def __init__(self, x, y, radius, vx = 0, vy = 0, mass = None):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(vx, vy)
        print(self.vel)
        self.radius = radius
        if mass == None:
            self.mass = radius / 2
        else:
            self.mass = mass


    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 0), (int(self.pos.x), int(self.pos.y)), int(self.radius), 0)


    def update_position(self, objects, timestep, G):
        acceleration = pygame.Vector2(0, 0)
        for object in objects:
            if object != self:
                relative_pos = object.pos - self.pos
                acceleration += G * object.mass / relative_pos.length_squared() * relative_pos.normalize()

                if relative_pos.length() <= self.radius + object.radius:
                    self.collision_calc(object, relative_pos)
                    acceleration = G * object.mass / (self.radius + object.radius)**2 * relative_pos.normalize()
                    relative_scale = relative_pos
                    relative_scale.scale_to_length(self.radius + object.radius)
                    self.pos = object.pos - relative_scale


        self.vel += acceleration * timestep
        self.pos += self.vel * timestep


    def collision_calc(self, object, relative_pos):
        # from equation
        normal_unit = relative_pos.normalize()                                      # unit vector normal to contact
        tangential_unit = pygame.Vector2(-normal_unit.y, normal_unit.x)             # tangential to contact

        # getting tangential and normal components of velocity for both objects
        v1n = normal_unit.dot(self.vel)
        v1t = tangential_unit.dot(self.vel)
        v2n = normal_unit.dot(object.vel)
        v2t = tangential_unit.dot(object.vel)

        # normal velocities after collision
        v1n_prime = (v1n*(self.mass - object.mass) + 2*object.mass*v2n)/(self.mass + object.mass) * normal_unit
        v2n_prime = (v2n*(object.mass - self.mass) + 2*self.mass*v1n)/(self.mass + object.mass) * normal_unit

        v1t_prime = v1t * tangential_unit
        v2t_prime = v2t * tangential_unit

        v1_prime = v1n_prime + v1t_prime
        v2_prime = v2n_prime + v2t_prime

        self.vel = v1_prime
        object.vel = v2_prime


class Game:
    def __init__(self, width, height, object_info=None):
        pygame.init()
        pygame.display.set_caption('skalle')
        self.screen_width = width
        self.screen_height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.object_info = object_info
        self.G = 10000


        if object_info:
            self.object_info = np.array(object_info)
            self.set_units()
            self.object_info[:, 0] = self.object_info[:, 0]/self.pixel_to_km + self.screen_width/2
            self.object_info[:, 1] = self.object_info[:, 1]/self.pixel_to_km + self.screen_height/2
            self.object_info[:, 2] = self.object_info[:, 2]/self.radius_scale
            self.object_info[:, 3] = self.object_info[:, 3]/self.pixel_to_km
            self.object_info[:, 4] = self.object_info[:, 4]/self.pixel_to_km
            self.object_info[:, 5] = self.object_info[:, 5] / self.mass_scale

            #SKASLLE FJERBN
            self.object_info[1, 4] = np.sqrt(self.G*self.object_info[0, 5]/self.object_info[1, 0])



        # fill background
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((250,250,250))


    def set_units(self):
        x_diff = np.max(self.object_info[:, 0]) - np.min(self.object_info[:, 0])
        y_diff = np.max(self.object_info[:, 1]) - np.min(self.object_info[:, 1])


        longest_axis = np.max([x_diff, y_diff])
        self.pixel_to_km = 2.1 * longest_axis / self.screen_height
        self.mass_scale =  np.max(self.object_info[:, 5]) / np.min(self.object_info[:, 5])
        self.radius_scale = np.max(self.object_info[:, 2]) / self.screen_height*10
        self.G = 6.674 * 10**(-17) * self.pixel_to_km / self.mass_scale                                                # [Nm^2/kg^2]



    def initialize_objects(self, number_of_objects):
        self.objects = []
        overlap = True


        for i in range(number_of_objects):
            if self.object_info == None:
                self.objects.append(Object(np.random.randint(0, self.screen_width), np.random.randint(0, self.screen_height), 5))#np.random.randint(5)))
                while overlap:
                    overlap = False
                    for object in self.objects:
                        if object != self.objects[i] and object != 0:
                            relative_pos = objects[i].pos - object.pos
                            if relative_pos.length() <= self.radius + object.radius:
                                overlap = True
                                self.objects[i].pos = pygame.Vector2(np.random.randint(0, self.screen_width), np.random.randint(0, self.screen_height))

            else:
                self.objects.append(Object(self.object_info[i][0], self.object_info[i][1], self.object_info[i][2], self.object_info[i][3], self.object_info[i][4], self.object_info[i][5]))

            self.objects[i].draw(self.background)


    def run(self):
        # blit everything to screen
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
        self.timestep = self.clock.tick(25) / 1000        # seconds


        # event loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()


            self.background.fill((250,250,250))


            for object in self.objects:
                object.update_position(self.objects, self.timestep, self.G)
                object.draw(self.background)



            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
            self.timestep = self.clock.tick(60) / 1000        # seconds


if __name__ == '__main__':
    game = Game(1500, 900)
    game.initialize_objects(number_of_objects=100)
    game.run()


    #earth_moon = [[0, 0, 6371.008, 0, 0, 5.97219 * 10**24], [396649, 0, 1737.4, 0, 1.02, 7.3459 * 10**22]]
    #game = Game(1500, 900, earth_moon)
    #game.initialize_objects(len(earth_moon))
    #game.run()


    """
    Earth Moon System:
    distance between: 396649 [km]

    EARTH STATS:
    5.97219 * 10**24 [kg]
    6371.008 [km]


    MOON STATS:
    7.3459 * 10**22 [kg]
    1737.4 [km]


    object info:
    [[x, y, r, vx, vy, mass], [x2, y2, r2, vx2, vy2, mass2]]


    """
