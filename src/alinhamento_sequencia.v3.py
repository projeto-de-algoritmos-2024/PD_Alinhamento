import pygame
import numpy as np
import time

WIDTH, HEIGHT = 900, 700
CELL_SIZE = 40
MARGIN = 50

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
DARK_GRAY = (50, 50, 50)

GAP_PENALTY = -1
MATCH_AWARD = 1
MISMATCH_PENALTY = -1

def sequence_alignment(seq1, seq2):
    rows, cols = len(seq2) + 1, len(seq1) + 1
    score_matrix = np.zeros((rows, cols))
    
    for i in range(rows):
        score_matrix[i][0] = i * GAP_PENALTY
    for j in range(cols):
        score_matrix[0][j] = j * GAP_PENALTY
    
    yield score_matrix.copy()
    
    for i in range(1, rows):
        for j in range(1, cols):
            match = score_matrix[i-1][j-1] + (MATCH_AWARD if seq1[j-1] == seq2[i-1] else MISMATCH_PENALTY)
            delete = score_matrix[i-1][j] + GAP_PENALTY
            insert = score_matrix[i][j-1] + GAP_PENALTY
            score_matrix[i][j] = max(match, delete, insert)
            
            yield score_matrix.copy()
    
    yield score_matrix

def find_sequence(score_matrix, seq1, seq2):
    align1, align2 = '', ''
    i, j = len(seq2), len(seq1)
    
    while i > 0 or j > 0:
        current_score = score_matrix[i][j]
        if i > 0 and j > 0 and (current_score == score_matrix[i-1][j-1] + (MATCH_AWARD if seq1[j-1] == seq2[i-1] else MISMATCH_PENALTY)):
            align1 = seq1[j-1] + align1
            align2 = seq2[i-1] + align2
            i -= 1
            j -= 1
        elif i > 0 and current_score == score_matrix[i-1][j] + GAP_PENALTY:
            align1 = '-' + align1
            align2 = seq2[i-1] + align2
            i -= 1
        else:
            align1 = seq1[j-1] + align1
            align2 = '-' + align2
            j -= 1
    
    return align1, align2

def draw_input_box(screen, font, text, x, y, active):
    color = GREEN if active else DARK_GRAY
    pygame.draw.rect(screen, color, (x, y, 400, 40), 2)
    text_surface = font.render(text, True, BLACK)
    screen.blit(text_surface, (x + 5, y + 5))

def draw_matrix(screen, matrix, seq1, seq2):
    font = pygame.font.Font(None, 30)
    for i in range(len(seq2) + 1):
        for j in range(len(seq1) + 1):
            x, y = MARGIN + j * CELL_SIZE, MARGIN + i * CELL_SIZE
            pygame.draw.rect(screen, GRAY, (x, y, CELL_SIZE, CELL_SIZE), 1)
            text = font.render(str(int(matrix[i, j])), True, BLACK)
            screen.blit(text, (x + 10, y + 5))
    
    for j, char in enumerate(seq1):
        screen.blit(font.render(char, True, BLUE), (MARGIN + (j + 1) * CELL_SIZE + 10, MARGIN - 30))
    for i, char in enumerate(seq2):
        screen.blit(font.render(char, True, RED), (MARGIN - 30, MARGIN + (i + 1) * CELL_SIZE + 10))

def draw_alignment(screen, align1, align2):
    font = pygame.font.Font(None, 40)
    y_offset = HEIGHT - 150
    x_offset = (WIDTH - len(align1) * 30) // 2
    
    for i, (char1, char2) in enumerate(zip(align1, align2)):
        color = GREEN if char1 == char2 else RED if char1 != '-' and char2 != '-' else GRAY
        char1_render = font.render(char1, True, color)
        char2_render = font.render(char2, True, color)
        
        screen.blit(char1_render, (x_offset + i * 30, y_offset))
        screen.blit(char2_render, (x_offset + i * 30, y_offset + 50))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Alinhamento de Sequências")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    seq1, seq2 = "", ""
    active_input = 1
    running = True
    
    while running:
        screen.fill(WHITE)
        draw_input_box(screen, font, "Seq1: " + seq1, 50, 50, active_input == 1)
        draw_input_box(screen, font, "Seq2: " + seq2, 50, 100, active_input == 2)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if active_input == 1:
                        active_input = 2
                    else:
                        running = False
                elif event.key == pygame.K_BACKSPACE:
                    if active_input == 1:
                        seq1 = seq1[:-1]
                    else:
                        seq2 = seq2[:-1]
                else:
                    if active_input == 1:
                        seq1 += event.unicode
                    else:
                        seq2 += event.unicode
        
        pygame.display.flip()
        clock.tick(30)
    
    generator = sequence_alignment(seq1, seq2)
    matrix = next(generator)
    alignment_shown = False
    align1, align2 = '', ''
    delay = 0.5
    running = True
    
    while running:
        screen.fill(WHITE)
        draw_matrix(screen, matrix, seq1, seq2)
        
        if alignment_shown:
            draw_alignment(screen, align1, align2)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        try:
            matrix = next(generator)
            time.sleep(delay)
        except StopIteration:
            if not alignment_shown:
                align1, align2 = find_sequence(matrix, seq1, seq2)
                alignment_shown = True
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
