Python 3.13.12 (tags/v3.13.12:1cbe481, Feb  3 2026, 18:22:25) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import React, { useState, useEffect } from 'react';
import { Chess, Square, Move } from 'chess.js';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, RotateCcw, Settings, ChevronDown } from 'lucide-react';

// Types
interface PieceProps {
  type: string;
  color: 'w' | 'b';
  square: string;
  isSelected?: boolean;
  isLegalMove?: boolean;
}

interface SquareProps {
  square: string;
  color: 'light' | 'dark';
  piece?: PieceProps;
  isSelected: boolean;
  isLegalMove: boolean;
  isCheck: boolean;
  onClick: () => void;
}

interface GameState {
  board: any;
  turn: 'w' | 'b';
  check: boolean;
  checkmate: boolean;
  stalemate: boolean;
}

// Enhanced Chess AI with multiple difficulty levels
class ChessAI {
  private depth: number;
  private pieceValues: { [key: string]: number } = {
    p: 100,
    n: 320,
    b: 330,
    r: 500,
    q: 900,
    k: 20000
  };

  constructor(difficulty: 'easy' | 'medium' | 'hard') {
    switch(difficulty) {
      case 'easy': this.depth = 2; break;
      case 'medium': this.depth = 3; break;
      case 'hard': this.depth = 4; break;
    }
  }

  private evaluateBoard(game: Chess): number {
    const board = game.board();
    let score = 0;

    for (let row = 0; row < 8; row++) {
      for (let col = 0; col < 8; col++) {
        const piece = board[row][col];
        if (piece) {
          const value = this.pieceValues[piece.type];
          const positionBonus = this.getPositionBonus(piece, row, col);
          const sign = piece.color === 'w' ? 1 : -1;
          score += (value + positionBonus) * sign;
        }
      }
    }
    return score;
  }

  private getPositionBonus(piece: any, row: number, col: number): number {
    // Center control bonus
    const centerDist = Math.abs(3.5 - col) + Math.abs(3.5 - row);
    return (8 - centerDist) * 5;
  }

  private minimax(
    game: Chess,
    depth: number,
    alpha: number,
    beta: number,
    isMaximizing: boolean
  ): { score: number; move?: Move } {
    if (depth === 0 || game.isGameOver()) {
      return { score: this.evaluateBoard(game) };
    }

    const moves = game.moves({ verbose: true });
    
    if (isMaximizing) {
      let maxScore = -Infinity;
      let bestMove: Move | undefined;

      for (const move of moves) {
        game.move(move);
        const { score } = this.minimax(game, depth - 1, alpha, beta, false);
        game.undo();

        if (score > maxScore) {
          maxScore = score;
          bestMove = move;
        }
        alpha = Math.max(alpha, score);
        if (beta <= alpha) break;
      }
      return { score: maxScore, move: bestMove };
    } else {
      let minScore = Infinity;
      let bestMove: Move | undefined;

      for (const move of moves) {
        game.move(move);
        const { score } = this.minimax(game, depth - 1, alpha, beta, true);
        game.undo();

        if (score < minScore) {
          minScore = score;
          bestMove = move;
        }
        beta = Math.min(beta, score);
        if (beta <= alpha) break;
      }
      return { score: minScore, move: bestMove };
    }
  }

  public getBestMove(game: Chess): Move | null {
    if (game.isGameOver()) return null;
    const result = this.minimax(game, this.depth, -Infinity, Infinity, game.turn() === 'w');
    return result.move || null;
  }
}

// 3D-like Piece Component with animations
const ChessPiece: React.FC<PieceProps> = ({ type, color, isSelected, isLegalMove }) => {
  const pieceSymbols: { [key: string]: string } = {
    k: '♚', q: '♛', r: '♜', b: '♝', n: '♞', p: '♟'
  };

  const whiteSymbols: { [key: string]: string } = {
    k: '♔', q: '♕', r: '♖', b: '♗', n: '♘', p: '♙'
  };

  const symbol = color === 'w' ? whiteSymbols[type] : pieceSymbols[type];
  const pieceColor = color === 'w' ? 'text-amber-100' : 'text-gray-900';
  
  return (
    <motion.div
      initial={{ scale: 0.8, y: -20 }}
      animate={{ 
        scale: 1, 
        y: 0,
        filter: isSelected ? 'drop-shadow(0 0 10px gold)' : 'none'
      }}
      whileHover={{ scale: 1.1 }}
      transition={{ type: "spring", stiffness: 300 }}
      className={`
        text-6xl cursor-pointer select-none
        ${pieceColor}
        ${isSelected ? 'text-yellow-300' : ''}
        drop-shadow-2xl
      `}
      style={{
        textShadow: color === 'b' 
          ? '2px 2px 4px rgba(255,255,255,0.2), -2px -2px 4px rgba(0,0,0,0.5)'
          : '2px 2px 4px rgba(0,0,0,0.3), -2px -2px 4px rgba(255,255,255,0.3)'
      }}
    >
      {symbol}
      {isLegalMove && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="absolute inset-0 rounded-full bg-green-500 opacity-30"
        />
      )}
    </motion.div>
  );
};

// Square Component with enhanced graphics
const Square: React.FC<SquareProps> = ({ 
  square, color, piece, isSelected, isLegalMove, isCheck, onClick 
}) => {
  const bgColor = color === 'light' 
    ? 'bg-gradient-to-br from-amber-200 to-amber-100' 
    : 'bg-gradient-to-br from-amber-800 to-amber-700';

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      transition={{ type: "spring", stiffness: 300 }}
      className={`
        relative aspect-square flex items-center justify-center
        ${bgColor}
        ${isSelected ? 'ring-4 ring-yellow-400 ring-inset' : ''}
        ${isCheck ? 'ring-4 ring-red-500 ring-inset animate-pulse' : ''}
        cursor-pointer shadow-inner
      `}
      onClick={onClick}
    >
      {isLegalMove && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="absolute w-4 h-4 bg-green-500 rounded-full opacity-50"
        />
      )}
      {piece && <ChessPiece {...piece} isSelected={isSelected} isLegalMove={isLegalMove} />}
      <span className="absolute bottom-0 left-1 text-xs opacity-30 font-mono">
        {square}
      </span>
    </motion.div>
  );
};

// Main Chess Game Component
const ChessGame: React.FC = () => {
  const [game, setGame] = useState(new Chess());
  const [selectedSquare, setSelectedSquare] = useState<string | null>(null);
  const [legalMoves, setLegalMoves] = useState<string[]>([]);
  const [gameState, setGameState] = useState<GameState>({
    board: game.board(),
    turn: 'w',
    check: false,
    checkmate: false,
    stalemate: false
  });
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium');
  const [ai, setAI] = useState<ChessAI>(new ChessAI('medium'));
  const [isAITurn, setIsAITurn] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [moveHistory, setMoveHistory] = useState<string[]>([]);

  useEffect(() => {
    setAI(new ChessAI(difficulty));
  }, [difficulty]);

  useEffect(() => {
    if (gameState.turn === 'b' && !gameState.checkmate && !gameState.stalemate) {
      setIsAITurn(true);
      const timer = setTimeout(() => makeAIMove(), 500);
      return () => clearTimeout(timer);
    } else {
      setIsAITurn(false);
    }
  }, [gameState.turn]);

  const updateGameState = (newGame: Chess) => {
    setGame(newGame);
    setGameState({
      board: newGame.board(),
      turn: newGame.turn(),
      check: newGame.isCheck(),
      checkmate: newGame.isCheckmate(),
      stalemate: newGame.isStalemate()
    });
  };

  const makeAIMove = () => {
    if (gameState.turn === 'b' && !gameState.checkmate && !gameState.stalemate) {
      const bestMove = ai.getBestMove(game);
      if (bestMove) {
        const newGame = new Chess(game.fen());
        newGame.move(bestMove);
        updateGameState(newGame);
        setMoveHistory(prev => [...prev, `Black: ${bestMove.san}`]);
        setSelectedSquare(null);
        setLegalMoves([]);
      }
    }
  };

  const handleSquareClick = (square: string) => {
    if (gameState.turn === 'b' || gameState.checkmate || gameState.stalemate || isAITurn) return;

    const piece = game.get(square as Square);

    // If a piece is selected and the clicked square is a legal move
    if (selectedSquare && legalMoves.includes(square)) {
      // Make the move
      const newGame = new Chess(game.fen());
      const move = newGame.move({
        from: selectedSquare as Square,
        to: square as Square,
        promotion: 'q' // Always promote to queen for simplicity
      });

      if (move) {
        updateGameState(newGame);
        setMoveHistory(prev => [...prev, `White: ${move.san}`]);
        setSelectedSquare(null);
        setLegalMoves([]);
      }
    }
    // If clicking on a piece of the current player's color
    else if (piece && piece.color === gameState.turn) {
      // Select the piece and calculate legal moves
      setSelectedSquare(square);
      const moves = game.moves({ 
        square: square as Square,
        verbose: true 
      });
      setLegalMoves(moves.map(m => m.to));
    } else {
      setSelectedSquare(null);
      setLegalMoves([]);
    }
  };

  const resetGame = () => {
    const newGame = new Chess();
    updateGameState(newGame);
    setSelectedSquare(null);
    setLegalMoves([]);
    setMoveHistory([]);
  };

  const getBoardWithCoordinates = () => {
    const board = [];
    const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
    const ranks = ['8', '7', '6', '5', '4', '3', '2', '1'];

    for (let i = 0; i < 8; i++) {
      const row = [];
      for (let j = 0; j < 8; j++) {
        const square = files[j] + ranks[i];
        const piece = game.get(square as Square);
        const squareColor = (i + j) % 2 === 0 ? 'light' : 'dark';
        
        row.push(
          <Square
            key={square}
            square={square}
            color={squareColor}
            piece={piece ? {
              type: piece.type,
              color: piece.color,
              square: square
            } : undefined}
            isSelected={selectedSquare === square}
            isLegalMove={legalMoves.includes(square)}
            isCheck={gameState.check && piece?.type === 'k' && piece?.color === gameState.turn}
            onClick={() => handleSquareClick(square)}
          />
        );
      }
      board.push(
        <div key={i} className="flex">
          {row}
        </div>
      );
    }
    return board;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center p-8">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gray-800 rounded-3xl shadow-2xl p-8"
      >
        <div className="flex gap-8">
          {/* Chess Board */}
          <div className="relative">
            <motion.div 
              className="rounded-2xl overflow-hidden shadow-2xl border-4 border-gray-700"
              animate={{ rotateY: gameState.turn === 'b' ? 180 : 0 }}
              transition={{ duration: 0.5 }}
            >
              {getBoardWithCoordinates()}
            </motion.div>
            
            {/* Game Status Overlay */}
            {(gameState.checkmate || gameState.stalemate) && (
              <motion.div
                initial={{ opacity: 0, scale: 0.5 }}
                animate={{ opacity: 1, scale: 1 }}
                className="absolute inset-0 bg-black bg-opacity-75 rounded-2xl flex items-center justify-center"
              >
                <div className="text-center">
                  <h2 className="text-4xl font-bold text-white mb-4">
                    {gameState.checkmate ? 'Checkmate!' : 'Stalemate!'}
                  </h2>
                  <p className="text-xl text-gray-300 mb-6">
                    {gameState.checkmate 
                      ? `${gameState.turn === 'w' ? 'Black' : 'White'} wins!` 
                      : 'It\'s a draw!'}
                  </p>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={resetGame}
                    className="bg-blue-500 text-white px-6 py-3 rounded-lg font-semibold"
                  >
                    New Game
                  </motion.button>
                </div>
              </motion.div>
            )}
          </div>

          {/* Side Panel */}
          <div className="w-80">
            <div className="bg-gray-700 rounded-2xl p-6 mb-6">
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <Sparkles className="text-yellow-400" />
                Game Status
              </h2>
              <div className="space-y-3">
                <div className="flex justify-between text-gray-300">
                  <span>Turn:</span>
                  <span className="font-bold text-white">
                    {gameState.turn === 'w' ? 'White' : 'Black'}
                    {gameState.check && ' (Check!)'}
                  </span>
                </div>
                <div className="flex justify-between text-gray-300">
                  <span>Difficulty:</span>
                  <select 
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value as any)}
                    className="bg-gray-600 text-white rounded px-2 py-1"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Move History */}
            <div className="bg-gray-700 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4">Move History</h3>
              <div className="h-64 overflow-y-auto">
                {moveHistory.map((move, index) => (
                  <motion.div
                    key={index}
...                     initial={{ opacity: 0, x: -20 }}
...                     animate={{ opacity: 1, x: 0 }}
...                     transition={{ delay: index * 0.05 }}
...                     className={`p-2 mb-1 rounded ${
...                       index % 2 === 0 ? 'bg-gray-600' : 'bg-gray-500'
...                     } text-white`}
...                   >
...                     {move}
...                   </motion.div>
...                 ))}
...               </div>
...             </div>
... 
...             {/* Controls */}
...             <div className="mt-6 flex gap-3">
...               <motion.button
...                 whileHover={{ scale: 1.05 }}
...                 whileTap={{ scale: 0.95 }}
...                 onClick={resetGame}
...                 className="flex-1 bg-blue-500 text-white px-4 py-3 rounded-xl font-semibold flex items-center justify-center gap-2"
...               >
...                 <RotateCcw size={20} />
...                 New Game
...               </motion.button>
...               <motion.button
...                 whileHover={{ scale: 1.05 }}
...                 whileTap={{ scale: 0.95 }}
...                 onClick={() => setShowSettings(!showSettings)}
...                 className="bg-gray-700 text-white px-4 py-3 rounded-xl"
...               >
...                 <Settings size={20} />
...               </motion.button>
...             </div>
...           </div>
...         </div>
...       </motion.div>
...     </div>
...   );
... };
... 
