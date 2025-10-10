import { GamePlayer, NewGame } from "./new-game";

export class NewGameFactory {

    public static createGame(playerId: string, anonymous: boolean, gameMode: 'single' | 'online', singleSide: 'red' | 'black' | null): NewGame {
        let newGame = new NewGame('New Game', new Date(), gameMode!);
        let players: GamePlayer[] = [];
        
        // with AI bot
        if (gameMode == 'single' && !!singleSide) {
            players.push(new GamePlayer(playerId, singleSide, true, anonymous));
        } else if (gameMode == 'online') {
            players.push(new GamePlayer(playerId, '', true, anonymous));
        }

        newGame.players = players;
    
        return newGame;
    }
}