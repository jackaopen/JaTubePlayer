import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import PlayerOverflow from './PlayerOverflow.js';
export default class PlayerControlsOverlay extends YTNode {
    static type = 'PlayerControlsOverlay';
    overflow;
    constructor(data) {
        super();
        this.overflow = Parser.parseItem(data.overflow, PlayerOverflow);
    }
}
//# sourceMappingURL=PlayerControlsOverlay.js.map