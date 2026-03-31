import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Button from './Button.js';
import MultiMarkersPlayerBar from './MultiMarkersPlayerBar.js';
export default class DecoratedPlayerBar extends YTNode {
    static type = 'DecoratedPlayerBar';
    player_bar;
    player_bar_action_button;
    constructor(data) {
        super();
        this.player_bar = Parser.parseItem(data.playerBar, MultiMarkersPlayerBar);
        this.player_bar_action_button = Parser.parseItem(data.playerBarActionButton, Button);
    }
}
//# sourceMappingURL=DecoratedPlayerBar.js.map