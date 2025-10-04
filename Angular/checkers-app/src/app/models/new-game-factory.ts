import { NewGame } from "./new-game";

export class NewGameFactory {

    public static createGame(playerId: string, gameMode: 'single' | 'multi' | 'online', singleSide: 'red' | 'black' | null): NewGame {
        let newGame = new NewGame('New Game', new Date(), gameMode!);
        
        if (gameMode == 'single' && !!singleSide) {
            switch (singleSide) {
                case 'red':
                    newGame.light_player = playerId;
                    newGame.dark_player = 'AI';
                    break;
                case 'black':
                    newGame.light_player = 'AI';
                    newGame.dark_player = playerId;
                    break;
            }
        } else if (gameMode == 'multi') {
            newGame.light_player = playerId;
            newGame.dark_player = playerId;
        } else if (gameMode == 'online') {
            newGame.light_player = playerId;
            newGame.dark_player = playerId;
        }
    
        return newGame;
    }
}