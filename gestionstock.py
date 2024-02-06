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
font = pygame.font.Font('atwriter.ttf', 17)
table_font = pygame.font.Font('atwriter.ttf', 12)  # Police pour le texte du tableau
title_font = pygame.font.Font('atwriter.ttf', 35)  # Utiliser la même police avec une taille de 30

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
        self.font = pygame.font.Font('atwriter.ttf', 12)
        self.txt_surface = font.render(text, True, WHITE)  # Utilisation de la police définie globalement
        self.active = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self == input_boxes[0]:  # Si c'est la box "Ajouter Produit"
                    process_add_product(self.text)
                elif self == input_boxes[1]:  # Si c'est la box "Supprimer Produit"
                    process_delete_product(self.text)
                elif self == input_boxes[2]:  # Si c'est la box "Modifier Produit"
                    process_modify_product(self.text)
                self.text = ''
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = font.render(self.text, True, WHITE)

    def draw(self, screen):
        # Mise à jour du texte à afficher avec la police ajustée
        self.txt_surface = self.font.render(self.text, True, WHITE)
        txt_rect = self.txt_surface.get_rect(center=self.rect.center)
        pygame.draw.rect(screen, BLACK, self.rect)
        screen.blit(self.txt_surface, txt_rect)
        pygame.draw.rect(screen, self.color, self.rect, 2)
        
class Store:
    def __init__(self, mydb):
        self.mydb = mydb

    def fetch_products(self):
        cursor = self.mydb.cursor()
        cursor.execute("SELECT * FROM product")
        products = cursor.fetchall()
        cursor.close()
        return products

    def ajouter_produit(self, name, decription, price, quantity, id_category):
        cursor = self.mydb.cursor()
        # La requête SQL doit maintenant utiliser 'name' au lieu de 'nom'.
        query = "INSERT INTO product (name, decription, price, quantity, id_category) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (name, decription, price, quantity, id_category))
        self.mydb.commit()
        cursor.close()

    def supprimer_produit_par_nom(self, name):
        cursor = self.mydb.cursor()
        query = "DELETE FROM product WHERE name = %s"
        cursor.execute(query, (name,))
        self.mydb.commit()
        cursor.close()

    def modifier_produit(self, name, new_decription, new_price, new_quantity, new_id_category):
        cursor = self.mydb.cursor()
        query = ("UPDATE product "
                 "SET decription = %s, price = %s, quantity = %s, id_category = %s "
                 "WHERE name = %s")
        cursor.execute(query, (new_decription, new_price, new_quantity, new_id_category, name))
        self.mydb.commit()
        cursor.close()

# Connexion à la base de données
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mars1993",
    database="store"
)

# Fonction pour traiter la saisie de l'utilisateur
def process_add_product(input_text):
    data = input_text.split(',')
    if len(data) >= 5:
        name, description, price, quantity, id_category = data
        store.ajouter_produit(name.strip(), description.strip(), price.strip(), quantity.strip(), id_category.strip())
    update_display()
    
def process_delete_product(input_text):
    name = input_text.strip()
    store.supprimer_produit_par_nom(name)
    update_display()

def process_modify_product(input_text):
    data = input_text.split(',')
    if len(data) >= 5:
        name, new_description, new_price, new_quantity, new_id_category = data
        store.modifier_produit(name.strip(), new_description.strip(), new_price.strip(), new_quantity.strip(), new_id_category.strip())
    update_display()

# Fonction pour mettre à jour l'affichage du tableau
def update_display():
    global products, screen, background, x_position, y_position, column_widths
    products = store.fetch_products()
    screen.fill(BLACK)
    screen.blit(background, (x_position, y_position))
    draw_table(products, 10, 300, column_widths)
    
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
products = store.fetch_products()

# Boucle principale
running = True
while running:
    screen.fill(BLACK)  # Remplir l'arrière-plan avec une couleur noire
    screen.blit(background, (x_position, y_position)) # Centrage horizontal de l'image
    
    # Préparer le texte du titre
    title_text = "La Grande Epicerie"
    title_surface = title_font.render(title_text, True, WHITE)
    title_x_position = screen_width // 2 - title_surface.get_width() // 2
    title_y_position = 30  # 20 pixels du haut

    # Dessiner le titre
    screen.blit(title_surface, (title_x_position, title_y_position))
    
    # Calculer la position y pour le texte supplémentaire sous chaque titre
    offset_y = 20  # Décalage vertical pour le texte supplémentaire
    vertical_shift = -15  # Remonter de 50px

    # Afficher les zones de texte et les textes avec un décalage vertical ajusté
    for i, box in enumerate(input_boxes):
        box.draw(screen)
        text_y_position = box.rect.y - 30 + vertical_shift  # 30 pixels au-dessus de la boîte (20 initialement - 10 pour le décalage)

        # Déterminer le texte à afficher pour chaque box
        if i == 0:
            title_text = 'Ajouter Produit'
            info_text = "(nom, description, prix, quantite, cat)"
        elif i == 1:
            title_text = 'Supprimer Produit'
            info_text = "(nom)"
        else:
            title_text = 'Modifier Produit'
            info_text = "(nom, new description, new prix, new quantite, new cat)"

        # Dessiner le titre
        text_surface = font.render(title_text, True, WHITE)
        text_x_position = screen_width // 2 - text_surface.get_width() // 2
        draw_text(title_text, text_x_position, text_y_position)

        # Dessiner les informations supplémentaires sous le titre
        info_text_surface = font.render(info_text, True, WHITE)
        info_text_x_position = screen_width // 2 - info_text_surface.get_width() // 2
        draw_text(info_text, info_text_x_position, text_y_position + offset_y)  # Ajuster la position y

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
