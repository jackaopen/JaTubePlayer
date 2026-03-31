import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Button from './Button.js';
import MenuTitle from './MenuTitle.js';
import PlaylistAddToOption from './PlaylistAddToOption.js';
export default class AddToPlaylist extends YTNode {
    static type = 'AddToPlaylist';
    actions;
    playlists;
    constructor(data) {
        super();
        this.actions = Parser.parseArray(data.actions, [MenuTitle, Button]);
        this.playlists = Parser.parseArray(data.playlists, PlaylistAddToOption);
    }
}
//# sourceMappingURL=AddToPlaylist.js.map