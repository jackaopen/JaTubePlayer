import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
export default class GameCard extends YTNode {
    static type = 'GameCard';
    game;
    constructor(data) {
        super();
        this.game = Parser.parseItem(data.game);
    }
}
//# sourceMappingURL=GameCard.js.map