import numpy as np

class Board:
    def __init__(self, state=None):
        if state is None:
            self.state = np.array([[0]*7 for _ in range(6)])
        elif state.shape == (6,7):
            self.state = state
        else:
            raise Exception("Bad init state")
    
    def copy(self):
        return Board(state=self.state.copy())
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        s = '----'*len(self.state[0]) + '-\n'
        for line in self.state:
            for col in line:
                piece = ("#", " ", "O")[col+1]
                s += f'| {piece} '
            s += '|\n'
            s += '----'*len(self.state[0]) + '-\n'
        for key in range(7):
            s += f'  {key} '
        return s
    
    def ev(self):
        def ecols(board):
            s = 0

            for col in np.transpose(board):
                for i in range(len(col)-3):
                    if -1 not in col[i:i+4]:
                        t = sum(col[i:i+4])
                        if t==4:
                            return 10000
                        s += t**3
            return s

        def erows(board):
            s = 0

            for row in board:
                for i in range(len(row)-3):
                    if -1 not in row[i:i+4]:
                        t = sum(row[i:i+4])
                        if t==4:
                            return 10000
                        s += t**3
            return s

        def ediags(board):
            Bi = board[:,::-1] # Antidiagonal
            s = 0

            for i in range(len(board) - 3):
                for j in range(len(board[0])-3):
                    d = board[i:i+4,j:j+4].diagonal()
                    di = Bi[i:i+4,j:j+4].diagonal()
                    if -1 not in d:
                        t = sum(d)
                        if t==4:
                            return 10000
                        s += t**3
                    if -1 not in di:
                        t = sum(di)
                        if t==4:
                            return 10000
                        s += t**3
            return s
        
        return max(min(ecols(self.state) + erows(self.state) + ediags(self.state) - ecols(-1*self.state) - erows(-1*self.state) - ediags(-1*self.state), 5000), -5000)
    
    def __getitem__(self, key):
        return self.state[key]
    
    def __setitem__(self, key, val):
        self.state[key] = val
    
    def __delitem__(self, key):
        del self.state[key]
    
    def winner(self):
        def cols(board):
            P = (board+1)/2 # Player pieces, 1/2 for empty, 0 for agent

            for col in np.transpose(P):
                for i in range(len(col)-3):
                    if sum(col[i:i+4]) == 4:
                        return True
            return False

        def rows(board):
            P = (board+1)/2 # Player pieces, 1/2 for empty, 0 for agent

            for row in P:
                for i in range(len(row)-3):
                    if sum(row[i:i+4]) == 4:
                        return True
            return False

        def diags(board):
            P = (board+1)/2 # Player pieces, 1/2 for empty, 0 for agent
            Pi = (board[:,::-1]+1)/2 # Antidiagonal

            for i in range(len(P) - 3):
                for j in range(len(P[0])-3):
                    if sum(P[i:i+4,j:j+4].diagonal()) == 4:
                        return True
                    if sum(Pi[i:i+4,j:j+4].diagonal()) == 4:
                        return True
            return False
        
        win_p1 = cols(self.state) or rows(self.state) or diags(self.state)
        win_p2 = cols(-1*self.state) or rows(-1*self.state) or diags(-1*self.state)
        
        return  win_p1, win_p2
    
    def won(self):
        p1, p2 = self.winner()
        return p1 or p2
    
    def legal(self):
        if self.won():
            return []
        else:
            return [i for i,val in enumerate(self.state[0]) if val==0]
    
    def turn(self):
        return sum(sum(self))*-2 + 1
    
    def drop(self, i, val=None):
        if i in self.legal():
            if val is None:
                val = sum(sum(self))*-2 + 1
            self[5-sum(abs(self[:,i])),i] = val
        else:
            raise Exception("This column is full")
        return self
    
    def alphabeta(self, depth, alpha, beta, player):
        if (depth == 0) or (self.won()) or (not self.legal()):
            return self.ev()
        if player == "player":
            value = -4999
            for action in self.legal():
                value = max(value, self.copy().drop(action).alphabeta(depth-1, alpha, beta, "agent"))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value + depth
        else:
            value=4999
            for action in self.legal():
                value = min(value, self.copy().drop(action).alphabeta(depth-1, alpha, beta, "player"))
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value - depth
    
    def agent(self, depth):
        if self.turn() == -1:
            a = [(action, self.copy().drop(action).alphabeta(depth, -4999, 4999, "player")) for action in self.legal()]
            return min(a, key=lambda x:x[1])[0]
        else:
            a = [(action, self.copy().drop(action).alphabeta(depth, -4999, 4999, "agent")) for action in self.legal()]
            return max(a, key=lambda x:x[1])[0]
    
    def play(self, player=0, difficulty=3):
        """
        player = -1 -> no bots
        player =  0 -> you play first
        player =  1 -> you play second
        """
        try:
            from IPython.display import clear_output
        except Exception as e:
            raise Exception("You must be using Jupyter/IPython to use the method play.")
        error = False
        while not self.won():
            clear_output(wait=False)
            print(self)
            if not self.legal():
                break
            if player == -1:
                if error:
                    print("Previous move was invalid")
                user_input = ''
                user_input = input(f'Choose a column to drop:')
                if user_input == 'exit':
                    return -1
                try:
                    self.drop(int(user_input))
                    error = False
                except Exception as e:
                    error = True
                    pass
            elif player == 0:
                if error:
                    print("Previous move was invalid")
                if self.turn() == 1:
                    user_input = ''
                    user_input = input(f'Choose a column to drop:')
                    if user_input == 'exit':
                        return -1
                    try:
                        self.drop(int(user_input))
                        error = False
                    except Exception as e:
                        error = True
                        pass
                else:
                    self.drop(self.agent(difficulty))
            else:
                if error:
                    print("Previous move was invalid")
                if self.turn() == -1:
                    user_input = ''
                    user_input = input(f'Choose a column to drop:')
                    if user_input == 'exit':
                        return -1
                    try:
                        self.drop(int(user_input))
                        error = False
                    except Exception as e:
                        error = True
                        pass
                else:
                    self.drop(self.agent(difficulty))
        clear_output(wait=False)
        print(self)
        if self.won():
            print(f"PLAYER {('O', '#')[int((self.turn()+1)/2)]} WINS!")
        else:
            print("Stalemate :(")
