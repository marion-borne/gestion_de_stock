import pygame
import mysql.connector
from pygame.locals import *

# Configuration de Pygame
pygame.init()
background = pygame.image.load("im2.jpg")
screen_width, screen_height = 600, 750
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Gestion de Stock')

# Couleurs
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)

# Police de caractères
font = pygame.font.Font('atwriter.ttf', 20)

# Fonctions d'interface
def draw_text(text, x, y, color=WHITE):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def draw_button(text, center_x, y, width, height):
    text_surface = font.render(text, True, WHITE)
    screen.blit(text_surface, (center_x - text_surface.get_width() // 2, y + height // 2 - text_surface.get_height() // 2))

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = BLACK
        self.text = text
        self.txt_surface = font.render(text, True, self.color)
        self.active = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = RED if self.active else BLACK
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.active = False
                    self.color = BLACK
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = font.render(self.text, True, self.color)

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

# Connexion à la base de données
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mars1993",
    database="store"
)

class Store:
    def __init__(self, mydb):
        self.mydb = mydb

    def fetch_products(self):
        cursor = self.mydb.cursor()
        cursor.execute("SELECT * FROM product")
        products = cursor.fetchall()
        cursor.close()
        return products

    def ajouter_produit(self, nom, description, price, quantity, id_category):
        cursor = self.mydb.cursor()
        cursor.execute("INSERT INTO product (nom, description, price, quantity, id_category) VALUES (%s, %s, %s, %s, %s)", (nom, description, price, quantity, id_category))
        self.mydb.commit()
        cursor.close()

    def supprimer_produit(self, id):
        cursor = self.mydb.cursor()
        cursor.execute("DELETE FROM product WHERE id = %s", (id,))
        self.mydb.commit()
        cursor.close()

    def modifier_produit(self, id, nom, description, price, quantity, id_category):
        cursor = self.mydb.cursor()
        cursor.execute("UPDATE product SET nom = %s, description = %s, price = %s, quantity = %s, id_category = %s WHERE id = %s", (nom, description, price, quantity, id_category, id))
        self.mydb.commit()
        cursor.close()

# Création de l'instance Store et des InputBox
store = Store(mydb)
espacement = 20
decalage_vertical = 100
input_boxes = [
    InputBox(screen_width // 2 - 100, 50 + decalage_vertical, 200, 30),
    InputBox(screen_width // 2 - 100, 50 + 60 + espacement + decalage_vertical, 200, 30),
    InputBox(screen_width // 2 - 100, 50 + 120 + 2 * espacement + decalage_vertical, 200, 30)
]

# Boucle principale
running = True
while running:
    screen.fill(GRAY)
    products = store.fetch_products()

    # Afficher les zones de texte et les textes avec un décalage vers le bas
    for i, box in enumerate(input_boxes):
        box.draw(screen)
        text_y_position = box.rect.y - 20  # 20 pixels au-dessus de la boîte

        if i == 0:
            text = 'Ajouter Produit'
        elif i == 1:
            text = 'Supprimer Produit'
        else:
            text = 'Modifier Produit'

        text_surface = font.render(text, True, WHITE)
        # Calculer la position x pour centrer le texte
        text_x_position = screen_width // 2 - text_surface.get_width() // 2
        draw_text(text, text_x_position, text_y_position)

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        for box in input_boxes:
            box.handle_event(event)

    pygame.display.update()

pygame.quit()
mydb.close()
