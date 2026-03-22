from superwires import games, color
import random

games.init(screen_width = 840, screen_height = 580, fps = 50)


class Dog(games.Sprite):
 
    image = games.load_image("ring.png")

    def __init__(self):
        """ Initialize Dog object and create Text object for score. """
        super(Dog, self).__init__(image = Dog.image,
                                  x = games.mouse.x,
                                  bottom = games.screen.height)
        self.scoreText = games.Text(value = "Score ", size = 25, color = color.black,
                                top = 5, right = games.screen.width - 200)
        games.screen.add(self.scoreText)
        self.score = games.Text(value = 0, size = 25, color = color.black,
                                top = 5, right = games.screen.width - 10)
        games.screen.add(self.score)

        self.levelText = games.Text(value = "Level ", size = 25, color = color.black,
                                top = 5, left = games.screen.width - 830)
        games.screen.add(self.levelText)
        
        self.level = games.Text(value = 0, size = 25, color = color.black,
                                top = 5, left = games.screen.width - 750)
        games.screen.add(self.level)

    def update(self):
        """ Move to mouse x position. """
        self.x = games.mouse.x
        
        if self.left < 0:
            self.left = 0
            
        if self.right > games.screen.width:
            self.right = games.screen.width
            
        self.check_catch()

    def check_catch(self):
        """ Check if catch balls. """
        for ball in self.overlapping_sprites:
            self.score.value += 10
            self.score.right = games.screen.width - 10 
            ball.handle_caught()
            """ Change game level. """
            if self.score.value == 400:
                self.level.value += 1
                self.level.left = games.screen.width - 800 
                """ Next level game. """
                level_message = games.Message(value = "Level 1",
                                    size = 90,
                                    color = color.green,
                                    x = games.screen.width/2,
                                    y = games.screen.height/2,
                                    lifetime = 1 * games.screen.fps)
                games.screen.add(level_message)
                
            if self.score.value == 700:
                self.level.value += 1
                self.level.left = games.screen.width - 800 
                """ Next level game. """
                level_message = games.Message(value = "Level 2",
                                    size = 90,
                                    color = color.purple,
                                    x = games.screen.width/2,
                                    y = games.screen.height/2,
                                    lifetime = 1 * games.screen.fps)
                games.screen.add(level_message)
            """ Complete game."""    
            if self.score.value == 950: 
                """ Win Message. """
                win_message = games.Message(value = "You Win",
                                    size = 90,
                                    color = color.pink,
                                    x = games.screen.width/2,
                                    y = games.screen.height/2,
                                    lifetime = 1 * games.screen.fps,
                                    after_death = games.screen.quit)
                games.screen.add(win_message)

class Ball(games.Sprite):
    """
    A ball which falls to the ground.
    """ 
    image = games.load_image("ball.png")
    speed = 3

    def __init__(self, x, y = 70):
        """ Initialize a Ball object. """
        super(Ball, self).__init__(image = Ball.image,
                                    x = x, y = y,
                                    dy = Ball.speed)

    def update(self):
        """ Check if bottom edge has reached screen bottom. """
        if self.bottom > games.screen.height:
            self.end_game()
            self.destroy()

    def handle_caught(self):
        """ Destroy self if caught. """
        self.destroy()
        

    def end_game(self):
        """ End the game. """
        end_message = games.Message(value = "Game Over",
                                    size = 90,
                                    color = color.red,
                                    x = games.screen.width/2,
                                    y = games.screen.height/2,
                                    lifetime = 2 * games.screen.fps,
                                    after_death = games.screen.quit)
        games.screen.add(end_message)

        
class Man(games.Sprite):
    """
    A man which moves left and right, dropping balls.
    """
    image = games.load_image("mn.png")

    def __init__(self, y = 122, speed = 4, odds_change = 200):
        """ Initialize the Man object. """
        super(Man, self).__init__(image = Man.image,
                                   x = games.screen.width / 2,
                                   y = y,
                                   dx = speed)
        
        self.odds_change = odds_change
        self.time_til_drop = 0


    def update(self):
        """ Determine if direction needs to be reversed. """
        if self.left < 0 or self.right > games.screen.width:
            self.dx = -self.dx
        elif random.randrange(self.odds_change) == 0:
           self.dx = -self.dx
                
        self.check_drop()


    def check_drop(self):
        """ Decrease countdown or drop ball and reset countdown. """
        if self.time_til_drop > 0:
            self.time_til_drop -= 1
        else:
            new_ball = Ball(x = self.x)
            games.screen.add(new_ball)

            self.time_til_drop = int(new_ball.height * 1.3 / Ball.speed) + 1


def main():
    """ Play the game. """
    wall_image = games.load_image("wall.jpg", transparent = False)
    games.screen.background = wall_image

    the_man = Man()
    games.screen.add(the_man)

    the_dog = Dog()
    games.screen.add(the_dog)

    games.mouse.is_visible = False

    games.screen.event_grab = True
    games.screen.mainloop()


main()
