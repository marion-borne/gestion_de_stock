import pygame
import mysql.connector
from pygame.locals import *

# Configuration de Pygame
pygame.init()
original_background = pygame.image.load("im1.jpg")
screen_width, screen_height = 600, 750
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Gestion de Stock')

# Obtention des dimensions de l'image
image_height = original_background.get_height()
image_width = original_background.get_width()

# Redimensionnement et centrage de l'image de fond avec agrandissement de 20%
scale_factor = (screen_height / image_height) * 1.2  # Augmenter le facteur d'échelle de 20%
new_width = int(image_width * scale_factor)
new_height = int(image_height * scale_factor)  # S'assurer que la hauteur est également ajustée
background = pygame.transform.scale(original_background, (new_width, new_height))

# Centrer l'image agrandie sur l'écran
x_position = (screen_width - new_width) // 2
y_position = (screen_height - new_height) // 2

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Police de caractères
font = pygame.font.Font('atwriter.ttf', 20)
table_font = pygame.font.Font('atwriter.ttf', 12)  # Police pour le texte du tableau

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
        self.color = WHITE  # Couleur du contour de la boîte
        self.text = text
        self.txt_surface = font.render(text, True, WHITE)  # Utilisation de la police définie globalement
        self.active = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = font.render(self.text, True, WHITE)  # Mise à jour avec la police spécifiée


    def draw(self, screen):
        # Calcul pour centrer le texte dans la boîte
        txt_rect = self.txt_surface.get_rect(center=self.rect.center)
        # Remplir le rectangle avec du noir
        pygame.draw.rect(screen, BLACK, self.rect)
        # Afficher le texte centré
        screen.blit(self.txt_surface, txt_rect)
        # Dessiner un contour blanc autour de la boîte
        pygame.draw.rect(screen, self.color, self.rect, 2)  # 2 est l'épaisseur du contour

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

# Connexion à la base de données
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mars1993",
    database="store"
)

def draw_table(data, top_left_x, top_left_y, column_widths):
    # Calculer la largeur totale du tableau
    total_width = sum(column_widths)
    # Centrer le tableau horizontalement
    top_left_x = (screen_width - total_width) // 2
    # Dessiner l'en-tête du tableau
    header = ['id', 'name', 'description', 'price', 'quantity', 'id_category']
    # Dessiner l'en-tête du tableau avec un décalage de 100 pixels vers le bas
    draw_header(top_left_x, top_left_y + 100, column_widths, header)

     # Dessiner les lignes du tableau avec un décalage de 100 pixels vers le bas
    y_offset = top_left_y + 130  # 30 pixels pour la hauteur de l'en-tête + 100 pixels de décalage
    for row in data:
        for index, item in enumerate(row):
            cell_x = top_left_x + sum(column_widths[:index])
            cell_width = column_widths[index]
            # Dessiner le fond noir de la cellule
            pygame.draw.rect(screen, BLACK, pygame.Rect(cell_x, y_offset, cell_width, 30))
            draw_cell(cell_x, y_offset, cell_width, str(item), BLACK)  # Passer BLACK comme couleur de fond
        y_offset += 30
        
def draw_header(x, y, widths, titles):
    for index, title in enumerate(titles):
        cell_x = x + sum(widths[:index])
        cell_width = widths[index]
        # Dessiner le fond noir du header
        pygame.draw.rect(screen, BLACK, pygame.Rect(cell_x, y, cell_width, 30))
        draw_cell(cell_x, y, cell_width, title, BLACK)  # Passer BLACK comme couleur de fond

def draw_cell(x, y, width, text, background_color):
    # Dessiner le fond de la cellule
    pygame.draw.rect(screen, background_color, pygame.Rect(x, y, width, 30))
    # Dessiner le texte de la cellule
    text_surface = table_font.render(text, True, WHITE)
    screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2, y + (30 - text_surface.get_height()) // 2))
    # Dessiner le contour de la cellule
    pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, width, 30), 1)

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
    screen.fill(BLACK)  # Remplir l'arrière-plan avec une couleur noire
    screen.blit(background, (x_position, y_position)) # Centrage horizontal de l'image

    # Afficher les zones de texte et les textes avec un décalage vertical ajusté
    for i, box in enumerate(input_boxes):
        box.draw(screen)
        text_y_position = box.rect.y - 30  # 30 pixels au-dessus de la boîte (20 initialement - 10 pour le décalage)

        if i == 0:
            text = 'Ajouter Produit'
        elif i == 1:
            text = 'Supprimer Produit'
        else:
            text = 'Modifier Produit'

        text_surface = font.render(text, True, WHITE)
        text_x_position = screen_width // 2 - text_surface.get_width() // 2
        draw_text(text, text_x_position, text_y_position)

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        for box in input_boxes:
            box.handle_event(event)
            
    products = store.fetch_products()
    column_widths = [50, 100, 150, 50, 70, 100]  # Exemple de largeurs de colonnes, à ajuster selon vos besoins
    draw_table(products, 10, 300, column_widths)  # Ajustez les positions x et y selon vos besoins

    pygame.display.update()

pygame.quit()
mydb.close()
