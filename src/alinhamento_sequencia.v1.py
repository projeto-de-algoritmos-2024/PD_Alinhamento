import pygame
import numpy as np
import time

WIDTH, HEIGHT = 900, 700
CELL_SIZE = 50
MARGIN = 80

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)

gap_penalty = -1
match_award = 1
mismatch_penalty = -1

def sequence_alignment(seq1, seq2):
    rows, cols = len(seq2) + 1, len(seq1) + 1
    score_matrix = np.zeros((rows, cols))
    
    for i in range(rows):
        score_matrix[i][0] = i * gap_penalty
    for j in range(cols):
        score_matrix[0][j] = j * gap_penalty
    
    yield score_matrix.copy()
    
    for i in range(1, rows):
        for j in range(1, cols):
            match = score_matrix[i-1][j-1] + (match_award if seq1[j-1] == seq2[i-1] else mismatch_penalty)
            delete = score_matrix[i-1][j] + gap_penalty
            insert = score_matrix[i][j-1] + gap_penalty
            score_matrix[i][j] = max(match, delete, insert)
            
            yield score_matrix.copy()
    
    yield score_matrix

def find_sequence(score_matrix, seq1, seq2):
    align1, align2 = '', ''
    i, j = len(seq2), len(seq1)
    
    while i > 0 or j > 0:
        current_score = score_matrix[i][j]
        if i > 0 and j > 0 and (current_score == score_matrix[i-1][j-1] + (match_award if seq1[j-1] == seq2[i-1] else mismatch_penalty)):
            align1 = seq1[j-1] + align1
            align2 = seq2[i-1] + align2
            i -= 1
            j -= 1
        elif i > 0 and current_score == score_matrix[i-1][j] + gap_penalty:
            align1 = '-' + align1
            align2 = seq2[i-1] + align2
            i -= 1
        else:
            align1 = seq1[j-1] + align1
            align2 = '-' + align2
            j -= 1
    
    return align1, align2

def draw_matrix(screen, matrix, seq1, seq2):
    font = pygame.font.Font(None, 30)
    for i in range(len(seq2) + 1):
        for j in range(len(seq1) + 1):
            x, y = MARGIN + j * CELL_SIZE, MARGIN + i * CELL_SIZE
            pygame.draw.rect(screen, GRAY, (x, y, CELL_SIZE, CELL_SIZE), 1)
            text = font.render(str(int(matrix[i, j])), True, BLACK)
            screen.blit(text, (x + 15, y + 10))
    
    for j, char in enumerate(seq1):
        screen.blit(font.render(char, True, BLUE), (MARGIN + (j + 1) * CELL_SIZE + 15, MARGIN - 40))
    for i, char in enumerate(seq2):
        screen.blit(font.render(char, True, RED), (MARGIN - 40, MARGIN + (i + 1) * CELL_SIZE + 15))

def draw_alignment(screen, align1, align2):
    font = pygame.font.Font(None, 40)
    y_offset = HEIGHT - 150
    pygame.draw.rect(screen, WHITE, (MARGIN, y_offset, WIDTH - 2*MARGIN, 100))
    screen.blit(font.render("Alinhamento:", True, BLACK), (MARGIN, y_offset))
    screen.blit(font.render(align1, True, GREEN), (MARGIN, y_offset + 40))
    screen.blit(font.render(align2, True, GREEN), (MARGIN, y_offset + 80))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Alinhamento de Sequências")
    clock = pygame.time.Clock()
    
    seq1 = input("Digite a primeira sequência: ")
    seq2 = input("Digite a segunda sequência: ")
    
    generator = sequence_alignment(seq1, seq2)
    matrix = next(generator)
    
    running = True
    alignment_shown = False
    align1, align2 = '', ''
    delay = 0.5  

    while running:
        screen.fill(WHITE)
        draw_matrix(screen, matrix, seq1, seq2)
        
        if alignment_shown:
            draw_alignment(screen, align1, align2)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    delay = max(0.1, delay - 0.1)  
                elif event.key == pygame.K_ESCAPE:
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
