import pygame
import threading
import time



class GameUI:

    EVENT_APPLICATION_QUIT = 0
    EVENT_DEPTH_BUTTON_PRESSED = 1
    EVENT_PRUNING_BUTTON_PRESSED = 2
    EVENT_FIELD_PRESSED = 3

    def __init__(self):
        self.board = GameBoard()
        self.pruning = True
        self.depth = 8
        
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode([800, 800])
        
        self.events = []
        self.running = True

    def getEvents(self):
        events = self.events.copy()
        self.events = []
        return events

    def draw(self):
        background_color = (255, 255, 255)
        line_color = (0, 0, 0)
        button_color = (128, 128, 128)
        text_color = (255, 255, 255)
        line_width = 6

        font = pygame.font.SysFont('monospace', 14)
        
        self.screen.fill(background_color)
            
        pygame.draw.line(self.screen, line_color, (100, 100), (700, 100), line_width)
        pygame.draw.line(self.screen, line_color, (700, 100), (700, 700), line_width)
        pygame.draw.line(self.screen, line_color, (700, 700), (100, 700), line_width)
        pygame.draw.line(self.screen, line_color, (100, 700), (100, 100), line_width)
        
        pygame.draw.line(self.screen, line_color, (100, 300), (700, 300), line_width)
        pygame.draw.line(self.screen, line_color, (100, 500), (700, 500), line_width)
        pygame.draw.line(self.screen, line_color, (300, 100), (300, 700), line_width)
        pygame.draw.line(self.screen, line_color, (500, 100), (500, 700), line_width)

        pygame.draw.rect(self.screen, button_color, ((100, 30), (250, 40)))
        label = font.render('Minimax depth: %s' % str(self.depth), False, text_color)
        self.screen.blit(label, (120, 40))

        pygame.draw.rect(self.screen, button_color, ((450, 30), (250, 40)))
        label = font.render('Alpha-Beta pruning: %s' % str(self.pruning), False, text_color)
        self.screen.blit(label, (470, 40))

        for x in range(3):
            for y in range(3):
                relative_x = 200 + x * 200
                relative_y = 600 - y * 200

                if self.board.getField((x, y)) == GameBoard.FIELD_X:
                    pygame.draw.line(self.screen, line_color, (relative_x - 80, relative_y - 80), (relative_x + 80, relative_y + 80), line_width)
                    pygame.draw.line(self.screen, line_color, (relative_x - 80, relative_y + 80), (relative_x + 80, relative_y - 80), line_width)
                elif self.board.getField((x, y)) == GameBoard.FIELD_O:
                     pygame.draw.circle(self.screen, line_color, (relative_x, relative_y), 80, line_width)

        

    def update(self):
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                self.running = False
                self.events.append([GameUI.EVENT_APPLICATION_QUIT, None])
                return
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    event_x, event_y = event.pos
                    
                    for x in range(3):
                        for y in range(3):
                            if 100 + x * 200  <= event_x <= 300 + x * 200 and 500 - y * 200 <= event_y <= 700 - y * 200:
                                self.events.append([GameUI.EVENT_FIELD_PRESSED, [x, y]])

                    if 100  <= event_x <= 350 and 30 <= event_y <= 70:
                        self.events.append([GameUI.EVENT_DEPTH_BUTTON_PRESSED, None])

                    if 450  <= event_x <= 700 and 30 <= event_y <= 70:
                        self.events.append([GameUI.EVENT_PRUNING_BUTTON_PRESSED, None])
                    
        self.draw()
        pygame.display.flip()

    def loop(self):
        fps = 60
        
        while self.running:
            self.update()
            self.clock.tick(fps)
        pygame.quit()



class GameLogic:

    def __init__(self):
        self.ui = GameUI()
        self.ai = GameAI()
        self.state = GameState()

        self.ai.minimax_depth = 8
        self.ui.depth = 8
        
        self.ai.alpha_beta_pruning_enabled = True
        self.ui.pruning = True

    def loop(self):
        running = True
        while running:
            if self.state.status != GameState.STATUS_ONGOING:
                for event in self.ui.getEvents():
                    
                    if event[0] == GameUI.EVENT_APPLICATION_QUIT:
                        running = False
                        break
                    
                    elif event[0] == GameUI.EVENT_FIELD_PRESSED:
                        starting_player = GameState.PLAYER_1
                        self.state = GameState(current_player=starting_player)
                        self.ui.board = self.state.board
                        break

                    elif event[0] == GameUI.EVENT_PRUNING_BUTTON_PRESSED:
                        pruning = not self.ai.alpha_beta_pruning_enabled
                        self.ai.alpha_beta_pruning_enabled = pruning
                        self.ui.pruning = pruning

                    elif event[0] == GameUI.EVENT_DEPTH_BUTTON_PRESSED:
                        depth = self.ai.minimax_depth + 1
                        if depth > 8:
                            depth = 0
                        self.ai.minimax_depth = depth
                        self.ui.depth = depth
                    
            else:
                if self.state.current_player == GameState.PLAYER_1:
                    for event in self.ui.getEvents():
                        
                        if event[0] == GameUI.EVENT_APPLICATION_QUIT:
                            running = False
                            break
                        
                        elif event[0] == GameUI.EVENT_FIELD_PRESSED:
                            move = event[1]
                            if move in self.state.getValidMoves():
                                self.state = self.state.getNextState(move)
                                self.ui.board = self.state.board
                            break

                        elif event[0] == GameUI.EVENT_PRUNING_BUTTON_PRESSED:
                            pruning = not self.ai.alpha_beta_pruning_enabled
                            self.ai.alpha_beta_pruning_enabled = pruning
                            self.ui.pruning = pruning

                        elif event[0] == GameUI.EVENT_DEPTH_BUTTON_PRESSED:
                            depth = self.ai.minimax_depth + 1
                            if depth > 8:
                                depth = 0
                            self.ai.minimax_depth = depth
                            self.ui.depth = depth
                        
                else:
                    for move in self.state.getValidMoves():
                        print(move, ":", self.ai.getScoreMinimax(self.state.getNextState(move)))
                    print()
                    move = self.ai.getBestMove(self.state)
                    self.state = self.state.getNextState(move)
                    self.ui.board = self.state.board



""" Stores the states of individual fields on a Tic Tac Toe board """
class GameBoard:

    FIELD_EMPTY = -1
    FIELD_X = 0
    FIELD_O = 1

    def __init__(self, array=None):
        if array == None:
            self.array = [[GameBoard.FIELD_EMPTY for x in range(3)] for y in range(3)]
        else:
            self.array = array

    def getField(self, position):
        x, y = position
        return self.array[y][x]

    def setField(self, position, value):
        x, y = position
        self.array[y][x] = value

    def copy(self):
        array = [[self.array[y][x] for x in range(3)] for y in range(3)]
        return GameBoard(array)

    """ Generator through all 3 field long lines that are relevant in Tic Tac Toe """
    def getLines(self):
        # Get rows
        for y in range(3):
            row = [self.getField([x, y]) for x in range(3)]
            yield row

        # Get columns
        for x in range(3):
            column = [self.getField([x, y]) for y in range(3)]
            yield column

        # Get diagonals
        diagonal_1 = [self.getField([i, i]) for i in range(3)]
        yield diagonal_1
        
        diagonal_2 = [self.getField([i, 2 - i]) for i in range(3)]
        yield diagonal_2

    def isFull(self):
        fields = [self.getField([x, y]) for x in range(3) for y in range(3)]
        return fields.count(GameBoard.FIELD_EMPTY) == 0

    

""" Describes a Tic Tac Toe state: board state and current player """
class GameState:

    PLAYER_1 = 1
    PLAYER_2 = 2

    STATUS_ONGOING = -1
    STATUS_PLAYER_1_WON = 1
    STATUS_PLAYER_2_WON = 2
    STATUS_TIE = 3
    
    def __init__(self, board=None, current_player=None):
        if board == None:
            self.board = GameBoard()
        else:
            self.board = board

        if current_player == None:
            self.current_player = GameState.PLAYER_1
        else:
            self.current_player = current_player

        # Check if any of the players has won in any of the lines
        for line in self.board.getLines():
            if line.count(GameBoard.FIELD_X) == 3:
                self.status = GameState.STATUS_PLAYER_1_WON
                break
            elif line.count(GameBoard.FIELD_O) == 3:
                self.status = GameState.STATUS_PLAYER_2_WON
                break
        # Check if it's a tie
        else:
            if self.board.isFull():
                self.status = GameState.STATUS_TIE
            else:
                self.status = GameState.STATUS_ONGOING

    """ returns a list of all positions that can be played """
    def getValidMoves(self):
        # No moves are valid if the game has ended
        if self.status != GameState.STATUS_ONGOING:
            return []

        # Otherwise return all empty fields
        moves = []
        for x in range(3):
            for y in range(3):
                if self.board.getField([x, y]) == GameBoard.FIELD_EMPTY:
                    moves.append([x, y])
        return moves

    """ return a new state that the game ends up in if position pos is played """
    def getNextState(self, position):
        # Figure out who the next player is, and what symbol corresponds to the current player
        if self.current_player == GameState.PLAYER_1:
            next_player = GameState.PLAYER_2
            symbol = GameBoard.FIELD_X
        else:
            next_player = GameState.PLAYER_1
            symbol = GameBoard.FIELD_O
        
        new_board = self.board.copy()
        new_board.setField(position, symbol)
        new_state = GameState(new_board, next_player)
        return new_state



""" An agent that can select moves intelligently based on the game state """
class GameAI:

    def __init__(self):
        self.alpha_beta_pruning_enabled = True
        self.minimax_depth = 8

    """ Determine the score of the state """
    def getScore(self, state):
        # Determine true score if the game has ended
        if state.status == GameState.STATUS_PLAYER_1_WON:
            return 100
        elif state.status == GameState.STATUS_PLAYER_2_WON:
            return -100
        elif state.status == GameState.STATUS_TIE:
            return 0

        # Otherwise determine score heuristically
        score = 0

        # Optimal player will win this round
        for line in state.board.getLines():
            if state.current_player == GameState.PLAYER_1 and line.count(GameBoard.FIELD_X) == 2 and line.count(GameBoard.FIELD_EMPTY) == 1:
                return 100
            elif state.current_player == GameState.PLAYER_2 and line.count(GameBoard.FIELD_O) == 2 and line.count(GameBoard.FIELD_EMPTY) == 1:
                return -100

        # Count lines that need to be defended
        count = 0
        if state.current_player == GameState.PLAYER_1:
            for line in state.board.getLines():
                if line.count(GameBoard.FIELD_O) == 2 and line.count(GameBoard.FIELD_EMPTY) == 1:
                    count += 1
            if count >= 2: # Optimal player will win next round
                return -100
            elif count == 1:
                score -= 10 # Defense required
        else:
            for line in state.board.getLines():
                if line.count(GameBoard.FIELD_X) == 2 and line.count(GameBoard.FIELD_EMPTY) == 1:
                    count += 1
            if count >= 2: # Optimal player will win next round
                return 100
            elif count == 1:
                score += 10 # Defense required

        # Count lines where a win could still happen
        for line in state.board.getLines():
            if line.count(GameBoard.FIELD_X) == 0:
                score -= 1
            if line.count(GameBoard.FIELD_O) == 0:
                score += 1
        return score

    """ Determine the score of the state recursively using the minimax algorithm """
    def getScoreMinimax(self, state, depth=None, alpha_beta=None):
        if depth == None:
            depth = self.minimax_depth
        
        # Return the score of the state if we've reached the maximum depth, or if the game has ended 
        if depth == 0 or state.status != GameState.STATUS_ONGOING:
            return self.getScore(state)

        # Otherwise determine the score recursively
        if alpha_beta == None:
            alpha_beta = [-float("inf"), float("inf")]

        alpha, beta = alpha_beta
        if state.current_player == GameState.PLAYER_1:
            best_score = -float("inf")
            new_alpha_beta = [best_score, beta]
        else:
            best_score = float("inf")
            new_alpha_beta = [alpha, best_score]

        # Iterate over possible moves, find better scores, prune according to alpha and beta
        for move in state.getValidMoves():
            next_state = state.getNextState(move)
            score = self.getScoreMinimax(next_state, depth - 1, new_alpha_beta)
            if state.current_player == GameState.PLAYER_1:
                if score > best_score:
                    best_score = score
                    new_alpha_beta = [best_score, beta]
                    if best_score >= beta and self.alpha_beta_pruning_enabled:
                        break
            else:
                if score < best_score:
                    best_score = score
                    new_alpha_beta = [alpha, best_score]
                    if best_score <= alpha and self.alpha_beta_pruning_enabled:
                        break
                    
        return best_score

    """ Return the optimal position to play based on the minimax scores """
    def getBestMove(self, state, depth=None):
        # Score each move
        moves = state.getValidMoves()
        scored_moves = {self.getScoreMinimax(state.getNextState(move), depth): move for move in moves}

        # Return the optimal move for the current player
        if state.current_player == GameState.PLAYER_1:
            return scored_moves[max(scored_moves.keys())]
        else:
            return scored_moves[min(scored_moves.keys())]



app = GameLogic()
threading.Thread(target=app.loop).start()
app.ui.loop()
